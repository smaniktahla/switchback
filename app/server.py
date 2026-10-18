"""Switchback MVP server (stdlib only): serves the map UI + candidates, and builds a ride route.

Route = start -> [chosen segment, drawn from its own OSM geometry] -> GraphHopper connector -> next segment ... -> end.
Only the connectors come from the routing engine, so the chosen roads' geometry is preserved exactly in the GPX.

  python app/server.py            # http://0.0.0.0:8940 ; GraphHopper at $SWITCHBACK_GH (default http://localhost:8989)
"""
import json
import math
import os
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
GH = os.environ.get("SWITCHBACK_GH", "http://localhost:8989")
PORT = int(os.environ.get("SWITCHBACK_PORT", "8940"))
DATA = json.load(open(HERE / "data" / "candidates.json"))
BY_ID = {c["id"]: c for c in DATA["candidates"]}


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


def build(req):
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

    cur = start
    for n, s in enumerate(req["segments"]):
        c = BY_ID[s["id"]]
        line = c["line"][::-1] if s.get("reverse") else c["line"]
        if hav_m(cur, line[0]) > 30:
            co, d, t = gh_route(cur, line[0], prof)
            add("connector", f"to {c['name']}", co, d, t, idx=n)
        d = sum(hav_m(a, b) for a, b in zip(line, line[1:]))
        mps = (c["metrics"].get("speed_median_mph") or 35) * 0.44704 * 0.85   # tagged limit (35 mph if untagged) x 0.85
        add("segment", f"{c['name']} {c['ref']}".strip(), line, d, secs=d / mps, idx=n)
        cur = line[-1]
        e = (c.get("ext_start") if s.get("reverse") else c.get("ext_end")) if s.get("ext") else None
        if e:       # continue along the same road (e.g. round the loop at the end of a dead-end road)
            xl = [cur] + e["line"]
            xd = sum(hav_m(a, b) for a, b in zip(xl, xl[1:]))
            add("segment", f"{c['name']} (continued)", xl, xd, secs=xd / mps, idx=n, ext=True)
            cur = xl[-1]
    if end and hav_m(cur, end) > 30:
        co, d, t = gh_route(cur, end, prof)
        add("connector", "to finish", co, d, t)
    return {"points": pts, "parts": parts, "minutes": round(sum(p["secs"] for p in parts) / 60), "km": round(sum(p["km"] for p in parts), 1),
            "connector_km": round(sum(p["km"] for p in parts if p["kind"] == "connector"), 1),
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


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(HERE), **k)

    def end_headers(self):          # never let the browser reuse a stale candidates.json or page after a rebuild
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if self.path in ("/", ""):
            self.send_response(302); self.send_header("Location", "/static/index.html"); self.end_headers(); return
        return super().do_GET()

    def do_POST(self):
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            if self.path == "/api/route":
                out = build(req)
            elif self.path == "/api/gpx":
                b = gpx(req["route"], req.get("name") or "Switchback ride").encode()
                self.send_response(200); self.send_header("Content-Type", "application/gpx+xml")
                self.send_header("Content-Disposition", 'attachment; filename="switchback-ride.gpx"')
                self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
                return
            else:
                return self.send_error(404)
            code = 200
        except Exception as e:
            out, code = {"error": str(e)}, 400
        b = json.dumps(out).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b)))
        self.end_headers(); self.wfile.write(b)


if __name__ == "__main__":
    print(f"Switchback on http://0.0.0.0:{PORT}  (GraphHopper: {GH}, {len(BY_ID)} candidates)")
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
