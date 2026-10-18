"""Switchback MVP server (stdlib only): serves the map UI + candidates, and builds a ride route.

Route = start -> [chosen segment, drawn from its own OSM geometry] -> GraphHopper connector -> next segment ... -> end.
Only the connectors come from the routing engine, so the chosen roads' geometry is preserved exactly in the GPX.

  python app/server.py            # http://0.0.0.0:8940 ; GraphHopper at $SWITCHBACK_GH (default http://localhost:8989)
"""
import json
import math
import os
import re
import sys
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
GH = os.environ.get("SWITCHBACK_GH", "http://localhost:8989")
PORT = int(os.environ.get("SWITCHBACK_PORT", "8940"))
DATA = json.load(open(HERE / "data" / "candidates.json"))
sys.path.insert(0, str(HERE.parent / "src"))
from store import ROAD_ID_BASE, ApiError, Store, check_password            # noqa: E402

AUTH_ON = os.environ.get("SWITCHBACK_AUTH", "on").lower() != "off"      # off = single-user mode (desktop / localhost), everyone is the owner
DATA_DIR = Path(os.environ.get("SWITCHBACK_DATA", HERE.parent / "data_private"))
SECURE_COOKIES = os.environ.get("SWITCHBACK_SECURE_COOKIES") == "1"
LEGACY_ROADS = DATA_DIR / "custom_roads.json"                           # pre-accounts hand-added roads, imported once into the first admin
STORE = Store(DATA_DIR / "switchback.db")
BY_ID = {c["id"]: c for c in DATA["candidates"]}


def import_legacy_roads(uid):
    try:
        old = json.load(open(LEGACY_ROADS))
    except Exception:
        return 0
    n = 0
    for c in old:
        for k in ("id", "manual", "shared", "mine", "added_by", "added_on", "where"):
            c.pop(k, None)
        STORE.add_road(uid, c.get("name", "My road"), c, True); n += 1
    LEGACY_ROADS.rename(LEGACY_ROADS.with_suffix(".imported"))
    return n


def owner_user():
    """Single-user mode: one admin account, created on demand, never needs a password."""
    u = STORE.one("SELECT * FROM users ORDER BY id LIMIT 1")
    if not u:
        import secrets
        uid = STORE.create_user("owner", secrets.token_urlsafe(24), "admin"); import_legacy_roads(uid); u = STORE.user(uid)
    return u


def cand_for(cid, user):
    """A base candidate, or a hand-added road the user is allowed to see."""
    if cid < ROAD_ID_BASE:
        return BY_ID[cid]
    for c in STORE.roads_for(user["id"]):
        if c["id"] == cid:
            return c
    raise ApiError(404, "That road is not available.")
ROADS = json.load(open(HERE / "data" / "roads.json")) if (HERE / "data" / "roads.json").exists() else {}
_GRAPHS = {}


def road_graph(fam):
    if fam not in _GRAPHS:
        adj, loc = {}, {}
        for w in ROADS.get(fam, []):
            for n, c in zip(w["n"], w["c"]):
                loc[n] = c
            for a, b, ca, cb in zip(w["n"], w["n"][1:], w["c"], w["c"][1:]):
                d = hav_m(ca, cb)
                adj.setdefault(a, []).append((b, d)); adj.setdefault(b, []).append((a, d))
        _GRAPHS[fam] = (adj, loc)
    return _GRAPHS[fam]


def along_road(fam, a, b, max_m=250000.0, snap_m=300.0):
    """Path (coords, metres) from a to b following only the road family's own ways, or None."""
    import heapq
    adj, loc = road_graph(fam)
    if not loc:
        return None
    near = lambda p: min(loc, key=lambda n: hav_m(loc[n], p))
    na, nb = near(a), near(b)
    if hav_m(loc[na], a) > snap_m or hav_m(loc[nb], b) > snap_m:
        return None
    dist, prev, pq = {na: 0.0}, {}, [(0.0, na)]
    while pq:
        d, n = heapq.heappop(pq)
        if n == nb:
            path = [n]
            while n in prev:
                n = prev[n]; path.append(n)
            return [loc[i] for i in path[::-1]], d
        if d > dist.get(n, 1e18) or d > max_m:
            continue
        for m, w in adj.get(n, ()):
            if d + w < dist.get(m, 1e18):
                dist[m] = d + w; prev[m] = n; heapq.heappush(pq, (d + w, m))
    return None


def hav_m(a, b):
    p1, p2 = math.radians(a[1]), math.radians(b[1])
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(b[0] - a[0]) / 2) ** 2
    return 2 * 6371008.8 * math.asin(math.sqrt(h))


def gh_route(a, b, profile="car"):
    body = json.dumps({"profile": profile, "points": [a, b], "points_encoded": False, "instructions": False}).encode()
    req = urllib.request.Request(GH + "/route", body, {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            p = json.load(r)["paths"][0]
    except urllib.error.HTTPError as e:
        msg = json.load(e).get("message", str(e)) if e.fp else str(e)
        raise RuntimeError(msg)
    except Exception as e:
        raise RuntimeError(f"GraphHopper unreachable at {GH}: {e}")
    return p["points"]["coordinates"], p["distance"], p["time"] / 1000


def custom_candidate(name, line):
    """Measure a hand-drawn stretch with the same geometry code as the scan; speed/interruptions/traffic stay unknown."""
    from switchback import rank
    km = sum(hav_m(a, b) for a, b in zip(line, line[1:])) / 1000
    m = {"length_km": round(km, 2), "deg_per_km": 0, "turns_per_km_45": 0, "radius_p50": 0, "frac_straight": 1, "corners_30_per_km": 0,
         "longest_corner_chain": 0, "hard_per_km": 0, "hard_events": {}, "pub_junctions_per_km": 0, "pub_junctions": 0, "crossings": 0,
         "longest_clear_m": round(km * 1000), "speed_median_mph": None, "speed_known_share": 0, "speed_mph_range": None, "aadt": None, "aadt_coverage": 0}
    try:
        import numpy as np
        from switchback.discover import corner_chains
        from switchback.geometry import Params, analyze, features
        lon = np.array([p[0] for p in line]); lat = np.array([p[1] for p in line]); P = Params()
        ser, corners, straights, _w, _r = analyze(lon, lat, P, window_sizes=(1000,), stride=500)
        v = ser.s[ser.valid]; f = features(ser, corners, straights, float(v.min()), float(v.max()), P)
        num = lambda x, d=0: d if x != x else x
        m.update(deg_per_km=round(num(f["deg_per_km"])), turns_per_km_45=round(num(f["turns_per_km_45"]), 1), radius_p50=round(num(f["radius_p50"])),
                 frac_straight=round(num(f["frac_straight"], 1), 2), **corner_chains(lon, lat))
    except Exception as e:
        print("custom road metrics unavailable:", e)
    comps = rank.components(m); comps["flow"] = rank.UNKNOWN          # interruptions were not measured
    return {"family": name, "name": name, "ref": "", "highway": "manual", "state": "", "where": "", "surface": "unknown",
            "note": "", "manual": True, "metrics": m, "components": {k: round(v, 3) for k, v in comps.items()},
            "score": round(rank.score(comps, DATA["weights"]), 3), "line": [[round(a, 5), round(b, 5)] for a, b in line],
            "ext_end": None, "ext_start": None, "events": {"hard": []}}


def trace(points):
    """Follow the roads between the clicked points (plain car routing) and return the joined line."""
    line, km = [], 0.0
    for a, b in zip(points, points[1:]):
        co, d, _t = gh_route(a, b, "car")
        co = [c[:2] for c in co]
        line += co[1:] if line else co; km += d / 1000
    return line, km


def build(req, user):
    prof = "motorcycle" if req.get("connectors") == "twisty" else "car"
    start, loop = req["start"], bool(req.get("loop", True))
    end = req.get("end") or (start if loop else None)
    pts, parts, legs = [], [], []     # parts: [{kind, label, i0, i1}] index ranges into pts

    def add(kind, label, coords, dist, secs=None, idx=-1, ext=False):
        coords = [list(c[:2]) for c in coords]
        if pts and coords and hav_m(pts[-1], coords[0]) < 1.0:
            coords = coords[1:]
        i0 = len(pts); pts.extend(coords)
        parts.append({"kind": kind, "label": label, "idx": idx, "ext": ext, "secs": secs or 0, "i0": i0, "i1": len(pts) - 1, "km": round(dist / 1000, 2), "min": None if secs is None else round(secs / 60)})

    cur, prev_c = start, None
    for n, s in enumerate(req["segments"]):
        c = cand_for(s["id"], user)
        line = c["line"][::-1] if s.get("reverse") else c["line"]
        mps = (c["metrics"].get("speed_median_mph") or 35) * 0.44704 * 0.85   # tagged limit (35 mph if untagged) x 0.85
        joined = None
        if prev_c and req.get("same_road", True) and prev_c.get("family") == c.get("family") and hav_m(cur, line[0]) > 30:
            joined = along_road(c["family"], cur, line[0])      # ride the road itself between the two pieces
        if joined:
            add("along", f"along {c['name']}", joined[0], joined[1], secs=joined[1] / mps, idx=n)
        elif hav_m(cur, line[0]) > 30:
            co, d, t = gh_route(cur, line[0], prof)
            add("connector", f"to {c['name']}", co, d, t, idx=n)
        d = sum(hav_m(a, b) for a, b in zip(line, line[1:]))
        add("segment", f"{c['name']} {c['ref']}".strip(), line, d, secs=d / mps, idx=n)
        cur = line[-1]
        e = (c.get("ext_start") if s.get("reverse") else c.get("ext_end")) if s.get("ext") else None
        if e:       # continue along the same road (e.g. round the loop at the end of a dead-end road)
            xl = [cur] + e["line"]
            xd = sum(hav_m(a, b) for a, b in zip(xl, xl[1:]))
            add("segment", f"{c['name']} (continued)", xl, xd, secs=xd / mps, idx=n, ext=True)
            cur = xl[-1]
        prev_c = c
    if end and hav_m(cur, end) > 30:
        co, d, t = gh_route(cur, end, prof)
        add("connector", "to finish", co, d, t)
    return {"points": pts, "parts": parts, "minutes": round(sum(p["secs"] for p in parts) / 60), "km": round(sum(p["km"] for p in parts), 1),
            "connector_km": round(sum(p["km"] for p in parts if p["kind"] == "connector"), 1),
            "along_km": round(sum(p["km"] for p in parts if p["kind"] == "along"), 1),
            "segment_km": round(sum(p["km"] for p in parts if p["kind"] == "segment"), 1)}


def gpx(route, name):
    o = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<gpx version="1.1" creator="switchback" xmlns="http://www.topografix.com/GPX/1/1">',
         f"<metadata><name>{escape(name)}</name></metadata>"]
    pts = route["points"]
    o.append(f'<wpt lat="{pts[0][1]:.6f}" lon="{pts[0][0]:.6f}"><name>Start</name></wpt>')
    for p in route["parts"]:
        if p["kind"] == "segment" and not p.get("ext"):
            a = pts[p["i0"]]
            o.append(f'<wpt lat="{a[1]:.6f}" lon="{a[0]:.6f}"><name>{escape(p["label"])}</name><desc>{p["km"]} km chosen road</desc></wpt>')
    o.append(f"<trk><name>{escape(name)}</name><trkseg>")
    o += [f'<trkpt lat="{p[1]:.6f}" lon="{p[0]:.6f}"/>' for p in pts]
    o.append("</trkseg></trk></gpx>")
    return "\n".join(o)


def ok_json(h, out, code=200, cookie=None):
    b = json.dumps(out, separators=(",", ":")).encode()
    h.send_response(code); h.send_header("Content-Type", "application/json"); h.send_header("Content-Length", str(len(b)))
    if cookie:
        h.send_header("Set-Cookie", cookie)
    h.end_headers(); h.wfile.write(b)


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(HERE), **k)

    def log_message(self, fmt, *args):      # keep tokens in invite/reset URLs out of the log
        super().log_message(fmt, *[re.sub(r"(invite|reset)=[^&\s]+", r"\1=***", x) if isinstance(x, str) else x for x in args])

    def end_headers(self):          # never let the browser reuse a stale page or data after a rebuild
        self.send_header("Cache-Control", "no-store"); self.send_header("X-Content-Type-Options", "nosniff"); self.send_header("X-Frame-Options", "DENY")
        super().end_headers()

    # ---- identity
    def token(self):
        for part in (self.headers.get("Cookie") or "").split(";"):
            k, _, v = part.strip().partition("=")
            if k == "sb_session":
                return v
        return None

    def user(self):
        return STORE.user_for_session(self.token()) if AUTH_ON else owner_user()

    def need(self, admin=False):
        u = self.user()
        if not u:
            raise ApiError(401, "Please sign in.")
        if admin and u["role"] != "admin":
            raise ApiError(403, "Admins only.")
        return u

    def cookie(self, token, clear=False):
        secure = SECURE_COOKIES or self.headers.get("X-Forwarded-Proto") == "https"
        return f"sb_session={'' if clear else token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={0 if clear else 30 * 86400}{'; Secure' if secure else ''}"

    def ip(self):
        return self.client_address[0]

    # ---- routes
    def do_GET(self):
        path = self.path.split("?")[0]
        try:
            if path == "/api/state":
                u = self.user()
                st = STORE.settings()
                return ok_json(self, {"auth": AUTH_ON, "setup": AUTH_ON and STORE.user_count() == 0, "user": STORE.public_user(u) if u else None,
                                      "settings": {"server_name": st["server_name"], "share_roads_default": st["share_roads_default"] == "1"}})
            if path == "/api/candidates":
                u = self.need()
                return ok_json(self, {**DATA, "candidates": DATA["candidates"] + STORE.roads_for(u["id"])})
            if path == "/api/users":
                self.need(admin=True)
                return ok_json(self, {"users": [STORE.public_user(x, False) for x in STORE.users()],
                                      "invites": [dict(r) for r in STORE.pending_invites()], "roads": [dict(r) for r in STORE.all_roads_admin()]})
            if path.startswith("/api/invite/"):
                r = STORE.peek_token(path.rsplit("/", 1)[1], "invite")
                return ok_json(self, {"role": r["role"]})
            if path.startswith("/api/reset/"):
                r = STORE.peek_token(path.rsplit("/", 1)[1], "reset")
                return ok_json(self, {"username": STORE.user(r["user_id"])["username"]})
        except ApiError as e:
            return ok_json(self, {"error": e.msg}, e.status)
        if path in ("/", ""):
            self.send_response(302); self.send_header("Location", "/static/index.html"); self.end_headers(); return
        if not path.startswith("/static/"):         # only the web UI is public; data and code are not
            return self.send_error(404)
        return super().do_GET()

    def do_POST(self):
        try:
            if self.headers.get("X-Requested-With") != "switchback":      # cross-site forms cannot set this header
                raise ApiError(403, "Bad request origin.")
            n = int(self.headers.get("Content-Length", 0))
            if n > 2_000_000:
                raise ApiError(413, "Request too large.")
            req = json.loads(self.rfile.read(n) or b"{}")
            p = self.path
            if p == "/api/setup":
                if not AUTH_ON or STORE.user_count():
                    raise ApiError(409, "Setup is already done.")
                if not STORE.check_setup_code(req.get("code")):
                    raise ApiError(403, "Wrong setup code. Look for it in the server log.")
                uid = STORE.create_user(req.get("username", ""), req.get("password", ""), "admin")
                import_legacy_roads(uid); STORE.x("DELETE FROM settings WHERE k='setup_code'")
                return ok_json(self, {"ok": True}, cookie=self.cookie(STORE.new_session(uid)))
            if p == "/api/login":
                u = STORE.login(req.get("username", ""), req.get("password", ""), self.ip())
                return ok_json(self, {"ok": True}, cookie=self.cookie(STORE.new_session(u["id"])))
            if p == "/api/logout":
                STORE.drop_session(self.token()); return ok_json(self, {"ok": True}, cookie=self.cookie("", clear=True))
            if p == "/api/accept":
                t = STORE.peek_token(req.get("token"), "invite")
                uid = STORE.create_user(req.get("username", ""), req.get("password", ""), t["role"] or "rider"); STORE.use_token(req["token"])
                return ok_json(self, {"ok": True}, cookie=self.cookie(STORE.new_session(uid)))
            if p == "/api/reset":
                t = STORE.peek_token(req.get("token"), "reset")
                STORE.set_password(t["user_id"], req.get("password", "")); STORE.use_token(req["token"])
                return ok_json(self, {"ok": True}, cookie=self.cookie(STORE.new_session(t["user_id"])))
            u = self.need()
            if p == "/api/password":
                full = STORE.user(u["id"])
                if not AUTH_ON or not check_password(req.get("old", ""), full["pw"]):
                    raise ApiError(403, "Current password is wrong.")
                STORE.set_password(u["id"], req.get("new", "")); return ok_json(self, {"ok": True}, cookie=self.cookie(STORE.new_session(u["id"])))
            if p == "/api/prefs":
                STORE.set_prefs(u["id"], req.get("prefs") or {}); return ok_json(self, {"ok": True})
            if p == "/api/route":
                return ok_json(self, build(req, u))
            if p == "/api/gpx":
                b = gpx(req["route"], req.get("name") or "Switchback ride").encode()
                self.send_response(200); self.send_header("Content-Type", "application/gpx+xml")
                self.send_header("Content-Disposition", 'attachment; filename="switchback-ride.gpx"')
                self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b); return
            if p == "/api/custom/preview":
                line, km = trace(req["points"]); return ok_json(self, {"line": line, "km": round(km, 2)})
            if p == "/api/custom":
                line = req.get("line") or trace(req["points"])[0]
                name = str(req.get("name", "")).strip()[:60] or "My road"
                shared = bool(req["shared"]) if "shared" in req else STORE.setting("share_roads_default") == "1"
                return ok_json(self, {"id": STORE.add_road(u["id"], name, custom_candidate(name, line), shared)})
            if p == "/api/custom/delete":
                STORE.delete_road(req["id"], u); return ok_json(self, {"ok": True})
            if p == "/api/custom/share":
                STORE.set_road_shared(req["id"], u, bool(req.get("shared"))); return ok_json(self, {"ok": True})
            # ---- admin
            self.need(admin=True)
            if p == "/api/invite":
                t, exp = STORE.create_token("invite", u["id"], role=req.get("role", "rider"), note=req.get("note", ""))
                return ok_json(self, {"token": t, "expires": exp})
            if p == "/api/users/create":
                uid = STORE.create_user(req.get("username", ""), req.get("password", ""), req.get("role", "rider")); return ok_json(self, {"id": uid})
            if p == "/api/users/password":
                STORE.set_password(req["id"], req.get("password", "")); return ok_json(self, {"ok": True})
            if p == "/api/users/reset-link":
                t, exp = STORE.create_token("reset", u["id"], user_id=req["id"]); return ok_json(self, {"token": t, "expires": exp})
            if p == "/api/users/role":
                STORE.set_role(req["id"], req.get("role")); return ok_json(self, {"ok": True})
            if p == "/api/users/disable":
                STORE.set_disabled(req["id"], bool(req.get("disabled"))); return ok_json(self, {"ok": True})
            if p == "/api/users/delete":
                STORE.delete_user(req["id"]); return ok_json(self, {"ok": True})
            if p == "/api/settings":
                for k, v in (req.get("settings") or {}).items():
                    STORE.set_setting(k, "1" if v is True else "0" if v is False else v)
                return ok_json(self, {"ok": True})
            return self.send_error(404)
        except ApiError as e:
            ok_json(self, {"error": e.msg}, e.status)
        except Exception as e:
            ok_json(self, {"error": str(e)}, 400)


def cli():
    """python app/server.py reset-password USER  -> sets a random password (for a locked-out admin)."""
    if len(sys.argv) >= 3 and sys.argv[1] == "reset-password":
        import secrets
        u = STORE.one("SELECT * FROM users WHERE username=?", sys.argv[2])
        if not u:
            sys.exit(f"No user named {sys.argv[2]}")
        pw = secrets.token_urlsafe(12); STORE.set_password(u["id"], pw)
        print(f"New password for {u['username']}: {pw}"); return True
    return False


if __name__ == "__main__":
    if cli():
        sys.exit(0)
    if AUTH_ON and STORE.user_count() == 0:
        print(f"\n  FIRST RUN: open the app and create the admin account.\n  Setup code: {STORE.setup_code()}\n")
    elif not AUTH_ON:
        owner_user()
    print(f"Switchback on http://0.0.0.0:{PORT}  (GraphHopper: {GH}, {len(BY_ID)} candidates, accounts {'on' if AUTH_ON else 'off'})", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
