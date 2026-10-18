"""M2b: compare GraphHopper's per-edge `curvature` with an independent calculation from OSM geometry.

Route along each reference road through waypoints every ~1 km, read the per-edge `curvature` and `edge_id`
path details, then (a) recompute beeline/length from the returned geometry, (b) recompute it from raw OSM
nodes split at junctions (no GraphHopper data structures), and compare both to GraphHopper's stored value.
Requires an ssh tunnel to the GraphHopper container (opened here).
"""
import json
import math
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import osmium
import pandas as pd
import requests
from scipy.stats import spearmanr
from shapely.geometry import LineString, Point

sys.path.insert(0, "src")
from switchback.geometry import Params, project
from switchback.reference import load_roads

DER, OUT = Path("data/derived"), Path("data/derived/gh_crosscheck")
URL = "http://127.0.0.1:18989"
R_GH = 6371000.0          # GraphHopper's DistanceCalcEarth radius
COUNT_IGNORED_AS_JUNCTIONS = True
FLOOR, STEP = 0.25, 0.05  # Curvature encoded value: 4 bits, min 0.25, factor 0.05 -> 0.25..1.0


def hav(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * R_GH * math.asin(math.sqrt(a))


def quantize(v):
    v = min(1.0, max(FLOOR, v))
    return FLOOR + STEP * round((v - FLOOR) / STEP)


def polylen(c):
    return sum(hav(*c[i], *c[i + 1]) for i in range(len(c) - 1))


def osm_tower_edges(pbf):
    """Edges between junction/end nodes of the highway ways in `pbf`, straight from OSM geometry."""
    ways, use = [], Counter()
    ignored = {"footway", "cycleway", "path", "pedestrian", "steps", "bridleway", "corridor"}   # as in config.yml
    other = Counter()   # node use by ways GraphHopper drops: trail/footway crossings still make a junction
    for o in osmium.FileProcessor(pbf, osmium.osm.NODE | osmium.osm.WAY).with_locations():
        if not o.is_way():
            continue
        pts = [(n.ref, n.lon, n.lat) for n in o.nodes]
        if o.tags.get("highway") in ignored:
            other.update(set(p[0] for p in pts))
            continue
        ways.append(pts)
        use.update(set(p[0] for p in pts))
    if COUNT_IGNORED_AS_JUNCTIONS:
        use.update(other)
    edges, dup = {}, set()
    for pts in ways:
        cut = [0] + [i for i in range(1, len(pts) - 1) if use[pts[i][0]] > 1] + [len(pts) - 1]
        for a, b in zip(cut, cut[1:]):
            seg = pts[a:b + 1]
            key = (seg[0][0], seg[-1][0])
            if key in edges or (key[1], key[0]) in edges:
                dup.add(key); dup.add((key[1], key[0]))
            edges[key] = [(x, y) for _, x, y in seg]
    return edges, dup


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tunnel = subprocess.Popen(["ssh", "-N", "-o", "ExitOnForwardFailure=yes", "-L", "18989:127.0.0.1:8989", os.environ.get("SWITCHBACK_GH_SSH_HOST", "localhost")])
    try:
        for _ in range(20):
            try:
                info = requests.get(f"{URL}/info", timeout=5).json(); break
            except Exception:
                time.sleep(1)
        else:
            raise SystemExit("no GraphHopper via tunnel")
        (OUT / "gh_info.json").write_text(json.dumps(info, indent=1))
        edges_osm, dup_keys = osm_tower_edges("data/gh/clip.osm.pbf")
        node_at = {}
        for (a, b), c in edges_osm.items():
            node_at[(round(c[0][0], 6), round(c[0][1], 6))] = a
            node_at[(round(c[-1][0], 6), round(c[-1][1], 6))] = b
        summary = {}
        for rid, cfg in load_roads().items():
            if "parent" in cfg:
                continue
            d = pd.read_csv(DER / rid / "centerline_nodes.csv")
            # Start/end only: intermediate via points would split GraphHopper edges with virtual edges.
            step = (cfg.get("gh_check") or {}).get("via_every_m")
            idx = [0, len(d) - 1] if not step else sorted(set(
                [int((d.cum_m - m).abs().idxmin()) for m in np.arange(0, d.cum_m.iloc[-1], step)] + [len(d) - 1]))
            wp = [[float(d.lon[i]), float(d.lat[i])] for i in idx]
            body = {"profile": "motorcycle", "points": wp, "points_encoded": False,
                    "instructions": False, "details": ["curvature", "edge_id"]}
            rc = (cfg.get("gh_check") or {}).get("only_road_class")
            if rc:   # keep snapping and routing on the reference road's class (avoids parallel service roads)
                body["custom_model"] = {"priority": [{"if": f"road_class != {rc}", "multiply_by": "0"}]}
            r = requests.post(f"{URL}/route", json=body, timeout=120).json()
            if "paths" not in r:
                raise SystemExit(f"{rid}: {r}")
            path = r["paths"][0]
            co = [(c[0], c[1]) for c in path["points"]["coordinates"]]
            cur = path["details"]["curvature"]; eid = path["details"]["edge_id"]
            # does the route follow the reference road?
            x, y, epsg = project(d.lon.values, d.lat.values)
            ref = LineString(np.c_[x, y])
            rx, ry, _ = project(np.array([c[0] for c in co]), np.array([c[1] for c in co]))
            dev = np.array([ref.distance(Point(a, b)) for a, b in zip(rx, ry)])
            wp_idx = {int(np.argmin([hav(*c, *w) for c in co])) for w in wp}
            rows = []
            for a, b, e in eid:
                seg = co[a:b + 1]
                L = polylen(seg)
                mine = hav(*seg[0], *seg[-1]) / L if L > 0.1 else 1.0
                gh = next(v for f, t, v in cur if f <= a < t)
                ka, kb = node_at.get((round(seg[0][0], 6), round(seg[0][1], 6))), node_at.get((round(seg[-1][0], 6), round(seg[-1][1], 6)))
                osm_c = None
                if ka is not None and kb is not None:
                    c = edges_osm.get((ka, kb)) or (edges_osm.get((kb, ka))[::-1] if (kb, ka) in edges_osm else None)
                    if c and (ka, kb) not in dup_keys:
                        Lo = polylen(c)
                        osm_c = hav(*c[0], *c[-1]) / Lo if Lo > 0.1 else 1.0
                rows.append({"edge_id": e, "i0": a, "i1": b, "length_m": L, "gh_curvature": gh,
                             "route_geom_ratio": mine, "osm_tower_ratio": osm_c,
                             "at_waypoint": a == 0 or b == len(co) - 1 or any(a <= w <= b for w in wp_idx),
                             "mid_lon": seg[len(seg) // 2][0], "mid_lat": seg[len(seg) // 2][1]})
            e = pd.DataFrame(rows)
            e["q_route"] = e.route_geom_ratio.map(quantize)
            e["q_osm"] = e.osm_tower_ratio.map(lambda v: quantize(v) if v == v and v is not None else np.nan)
            e.to_csv(OUT / f"{rid}_edges.csv", index=False)
            core = e[~e.at_waypoint]
            s = {"route_m": path["distance"], "reference_m": float(d.cum_m.iloc[-1]),
                 "via_points": len(wp), "max_dev_from_reference_m": float(dev.max()),
                 "p99_dev_m": float(np.percentile(dev, 99)), "frac_route_pts_dev_gt_20m": float((dev > 20).mean()),
                 "n_edges": len(e), "n_core_edges": len(core),
                 "match_exact_route_geom": float((np.isclose(core.q_route, core.gh_curvature)).mean()),
                 "match_exact_osm_towers": float((np.isclose(core.q_osm, core.gh_curvature)).mean()),
                 "osm_towers_found": float(core.q_osm.notna().mean()),
                 "mean_abs_diff_raw_vs_gh": float((core.route_geom_ratio.clip(FLOOR, 1) - core.gh_curvature).abs().mean()),
                 # Distribution uses ALL edges: a via point cuts an edge into pieces that all carry the same
                 # stored value, whereas dropping those edges would bias toward short edges.
                 "gh_value_levels_length_weighted": {f"{v:.2f}": float(w / e.length_m.sum()) for v, w in
                                                      e.groupby(e.gh_curvature.round(2)).length_m.sum().items()},
                 "frac_length_at_floor_0.25": float(e[e.gh_curvature <= 0.2501].length_m.sum() / e.length_m.sum()),
                 "median_edge_length_m": float(core.length_m.median()), "max_edge_length_m": float(core.length_m.max())}
            summary[rid] = s
        (OUT / "summary.json").write_text(json.dumps(summary, indent=1))
        print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "gh_value_levels_length_weighted"} for k, v in summary.items()}, indent=1))
        for k, v in summary.items():
            print(k, "levels:", v["gh_value_levels_length_weighted"])
    finally:
        tunnel.terminate()


if __name__ == "__main__":
    main()
