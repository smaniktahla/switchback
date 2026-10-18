"""MVP candidate discovery: reuse the Phase-1 geometry scan with generic 'twisty enough' bounds, then attach
context (interruptions, speed environment, corner chains, traffic). Descriptive only; ranking lives in rank.py."""
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from .geometry import Params, build_series, segment

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from scan_region import scan_chain   # noqa: E402  (Phase-1 scan; module-level code is definitions only)

from .scan import chain_ways  # noqa: E402

P = Params()


def generic_rng(d):
    inf = 1e9
    r = {"deg_per_km": (d["min_deg_per_km"], inf), "radius_p50": (0.0, d["max_radius_p50_m"]),
         "turns_per_km_45": (d["min_turns_per_km_45"], inf), "frac_straight": (0.0, d["max_frac_straight"])}
    return {"loose": r, "strict": r}


def scan(ways_pkl, cfg, workers=4, min_m=3000.0):
    ways, _places = pickle.load(open(ways_pkl, "rb"))
    chains = chain_ways(ways)
    long_ = [c for c in chains if sum(a[0] for a in c["attrs"]) >= min_m]
    state_of = {w["id"]: w["state"] for w in ways}
    rng = generic_rng(cfg["discovery"])
    jobs = [(i, c["key"], c["highway"], state_of[c["way_ids"][0]], c["pts"], rng) for i, c in enumerate(long_)]
    res = []
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for r in ex.map(scan_chain, jobs, chunksize=20):
            res += r
    return res, long_


def _hav_km(lon1, lat1, lon2, lat2):
    return float(np.hypot((lon2 - lon1) * 111.32 * np.cos(np.radians(lat1)), (lat2 - lat1) * 110.57))


def dedupe(res, min_km):
    """Keep the stretch with the highest heading change when two overlap on a chain or sit within min_km."""
    order = sorted(res, key=lambda r: -r["deg_per_km"])
    keep = []
    for r in order:
        mx, my = r["lon"][len(r["lon"]) // 2], r["lat"][len(r["lat"]) // 2]
        ok = True
        for k in keep:
            kx, ky = k["lon"][len(k["lon"]) // 2], k["lat"][len(k["lat"]) // 2]
            if _hav_km(mx, my, kx, ky) < min_km:
                ok = False; break
            if r["chain_idx"] == k["chain_idx"] and min(r["s1"], k["s1"]) - max(r["s0"], k["s0"]) > 0.3 * min(r["length_m"], k["length_m"]):
                ok = False; break
        if ok:
            keep.append(r)
    return keep


def merge_adjacent(res, gap_m=300.0):
    """Join stretches that sit on the same chain and are separated by at most gap_m (a scan run that a weak window split)."""
    out = []
    for r in sorted(res, key=lambda r: (r["chain_idx"], r["s0"])):
        if out and out[-1]["chain_idx"] == r["chain_idx"] and r["s0"] - out[-1]["s1"] <= gap_m:
            a = out[-1]; la, lb = a["length_m"], r["length_m"]; w = lambda k: (a[k] * la + r[k] * lb) / (la + lb)
            a.update({k: w(k) for k in ("deg_per_km", "radius_p50", "turns_per_km_45", "turns_per_km_15", "frac_straight", "frac_R_lt_50")},
                     straight_max_m=max(a["straight_max_m"], r["straight_max_m"]), s1=r["s1"], length_m=r["s1"] - a["s0"],
                     lon=a["lon"] + r["lon"], lat=a["lat"] + r["lat"])
        else:
            out.append(dict(r))
    return out


def bridge_path(ways, key, n_from, n_to, max_m=400.0):
    """Shortest run of OSM nodes joining two nodes along ways with the same road key (a short way that a junction
    cut out of the scanned chains). Returns [(id, lon, lat), ...] excluding both end nodes, or None."""
    import heapq
    adj, loc = {}, {}
    for w in ways:
        if (w["ref"] or w["name"] or f"unnamed:{w['id']}") != key:
            continue
        for p in w["pts"]:
            loc[p[0]] = p
        for a, b in zip(w["pts"], w["pts"][1:]):
            d = float(np.hypot((b[1] - a[1]) * 90000, (b[2] - a[2]) * 110570))
            adj.setdefault(a[0], []).append((b[0], d)); adj.setdefault(b[0], []).append((a[0], d))
    dist, prev, pq = {n_from: 0.0}, {}, [(0.0, n_from)]
    while pq:
        d, n = heapq.heappop(pq)
        if n == n_to:
            path = []
            while n in prev:
                n = prev[n]; path.append(n)
            return [loc[i] for i in path[::-1] if i != n_from]
        if d > dist.get(n, 1e18) or d > max_m:
            continue
        for m, w in adj.get(n, []):
            if d + w < dist.get(m, 1e18):
                dist[m] = d + w; prev[m] = n; heapq.heappush(pq, (d + w, m))
    return None


def merge_touching(stretches, roads, gap_m=250.0, ways=None):
    """Join stretches with the same road key whose ends meet within gap_m even though the scan saw them as separate
    chains (e.g. a side road splits the chain). Node lists and series are oriented end-to-start before joining."""
    def hav(a, b):
        return float(np.hypot((b[0] - a[0]) * 90000, (b[1] - a[1]) * 110570))

    items = [(dict(s), dict(r)) for s, r in zip(stretches, roads)]
    merged = True
    while merged:
        merged = False
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                (sa, ra), (sb, rb) = items[i], items[j]
                if sa["road_key"] != sb["road_key"]:
                    continue
                ea = [(ra["node_lon"][0], ra["node_lat"][0]), (ra["node_lon"][-1], ra["node_lat"][-1])]
                eb = [(rb["node_lon"][0], rb["node_lat"][0]), (rb["node_lon"][-1], rb["node_lat"][-1])]
                g, ia, ib = min((hav(ea[x], eb[y]), x, y) for x in (0, 1) for y in (0, 1))
                if g > gap_m:
                    continue
                if ia == 0:
                    for k in ("node_ids", "node_lon", "node_lat"):
                        ra[k] = ra[k][::-1]
                    sa["lon"], sa["lat"] = sa["lon"][::-1], sa["lat"][::-1]
                if ib == 1:
                    for k in ("node_ids", "node_lon", "node_lat"):
                        rb[k] = rb[k][::-1]
                    sb["lon"], sb["lat"] = sb["lon"][::-1], sb["lat"][::-1]
                la, lb = sa["length_m"], sb["length_m"]
                w = lambda k: (sa[k] * la + sb[k] * lb) / (la + lb)
                sa.update({k: w(k) for k in ("deg_per_km", "radius_p50", "turns_per_km_45", "turns_per_km_15", "frac_straight", "frac_R_lt_50")},
                          straight_max_m=max(sa["straight_max_m"], sb["straight_max_m"]), length_m=la + lb,
                          lon=sa["lon"] + sb["lon"], lat=sa["lat"] + sb["lat"])
                mid = bridge_path(ways, sa["road_key"], ra["node_ids"][-1], rb["node_ids"][0]) if ways else None
                if mid:       # fill the gap with the road's own nodes so the line follows the actual road
                    ra["node_ids"] += [p[0] for p in mid]; ra["node_lon"] += [p[1] for p in mid]; ra["node_lat"] += [p[2] for p in mid]
                for k in ("node_ids", "node_lon", "node_lat"):
                    ra[k] = ra[k] + rb[k]
                items[i] = (sa, ra); del items[j]; merged = True
                break
            if merged:
                break
    return [x[0] for x in items], [x[1] for x in items]


def stretch_nodes(chain, lon, lat, s0, s1, tol_m=300.0):
    """OSM node ids of the chain for the stretch [s0, s1] (metres along the chain). The nearest-node search is
    restricted to nodes near those chain positions, so loops (start and end at the same place) stay unambiguous."""
    cl = np.array([p[1] for p in chain["pts"]]); ca = np.array([p[2] for p in chain["pts"]])
    cum = np.r_[0.0, np.cumsum(np.hypot(np.diff(cl) * 111320 * np.cos(np.radians(ca[:-1])), np.diff(ca) * 110570))]

    def nearest(x, y, pos):
        ok = np.where(np.abs(cum - pos) <= tol_m + 0.03 * pos)[0]
        return int(ok[np.argmin(np.hypot((cl[ok] - x) * 90000, (ca[ok] - y) * 110570))])

    i0, i1 = nearest(lon[0], lat[0], s0), nearest(lon[-1], lat[-1], s1)
    a, b = sorted((i0, i1))
    pts = chain["pts"][a:b + 1]
    return {"node_ids": [p[0] for p in pts], "node_lon": [p[1] for p in pts], "node_lat": [p[2] for p in pts]}


def corner_chains(lon, lat):
    ser = build_series(lon, lat, P)
    corners, _ = segment(ser, P)
    c = corners[(~corners.partial) & (corners.angle_deg >= 30)].sort_values("s_start")
    km = float(ser.step[ser.valid].sum()) / 1000
    chains, cur = [], 1
    for g in (c.s_start.values[1:] - c.s_end.values[:-1]):
        if g <= 100:
            cur += 1
        else:
            chains.append(cur); cur = 1
    if len(c):
        chains.append(cur)
    return {"corners_30_per_km": round(len(c) / km, 2), "longest_corner_chain": int(max(chains)) if chains else 0}


def way_graph(ways, keys):
    """Adjacency (node -> neighbour nodes) and node locations, per road key, from the scan's ways."""
    adj = {k: {} for k in keys}; loc = {}
    for w in ways:
        k = w["ref"] or w["name"] or f"unnamed:{w['id']}"
        if k not in adj:
            continue
        for p in w["pts"]:
            loc[p[0]] = (p[1], p[2])
        for a, b in zip(w["pts"], w["pts"][1:]):
            adj[k].setdefault(a[0], set()).add(b[0]); adj[k].setdefault(b[0], set()).add(a[0])
    return adj, loc


def continue_road(adj, loc, seg_ids, cur, prev, max_m=12000.0):
    """Follow the same road on from a stretch's end (cur, arrived from prev) until it dead-ends, comes back onto the
    stretch or itself (a loop), or max_m. Returns {line, km, loop} or None when the road does not go on."""
    seg, visited, out, total, loop = set(seg_ids), set(seg_ids), [], 0.0, False
    def d(a, b):
        return float(np.hypot((loc[b][0] - loc[a][0]) * 90000, (loc[b][1] - loc[a][1]) * 110570))
    def brg(a, b):
        return np.arctan2((loc[b][0] - loc[a][0]) * 90000, (loc[b][1] - loc[a][1]) * 110570)
    while total < max_m:
        nb = [m for m in adj.get(cur, ()) if m != prev]
        if not nb:
            break
        if len(nb) > 1:      # a junction on the same road: keep going as straight as possible
            h = brg(prev, cur); nb.sort(key=lambda m: abs((brg(cur, m) - h + np.pi) % (2 * np.pi) - np.pi))
        nxt = nb[0]
        total += d(cur, nxt); out.append(nxt)
        if nxt in visited:
            loop = nxt in seg
            break
        visited.add(nxt); prev, cur = cur, nxt
    if not out or total < 150:
        return None
    return {"line": [[round(loc[n][0], 5), round(loc[n][1], 5)] for n in out], "km": round(total / 1000, 2), "loop": bool(loop)}
