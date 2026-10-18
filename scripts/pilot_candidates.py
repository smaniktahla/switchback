"""Context + geometry summary for a few candidate stretches, to choose pilot rides."""
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src"); sys.path.insert(0, "scripts")
from switchback.roadctx import analyse, read_context
from switchback.scan import chain_ways
import run_context as rc

D = Path("data/derived")
ways, _ = pickle.load(open(D / "scan_dc/region_ways.pkl", "rb"))
res, _, _ = pickle.load(open(D / "scan_dc/stretches_loose.pkl", "rb"))
ded = pd.read_csv(D / "scan_dc/all_deduped_stretches.csv")
chains = chain_ways(ways); long_ = [c for c in chains if sum(a[0] for a in c["attrs"]) >= 3000.0]
stretch = {(r["chain_idx"], round(r["s0"], 1), round(r["s1"], 1)): r for r in res}
picks = [int(x) for x in sys.argv[1:]]
out = {}
for rank in picks:
    row = ded[ded["rank"] == rank].iloc[0]; r = stretch[(int(row.chain_idx), round(row.s0, 1), round(row.s1, 1))]; ch = long_[int(row.chain_idx)]
    pts = np.array([(p[0], p[1], p[2]) for p in ch["pts"]])
    raw = np.r_[0.0, np.cumsum([np.hypot((pts[i + 1, 1] - pts[i, 1]) * 86800, (pts[i + 1, 2] - pts[i, 2]) * 111200) for i in range(len(pts) - 1)])]
    def locate(lon, lat, s):
        win = np.abs(raw - s) <= max(0.06 * s, 250.0); d = np.hypot(pts[:, 1] - lon, pts[:, 2] - lat); d[~win] = 1e9; return int(np.argmin(d))
    i0, i1 = locate(r["lon"][0], r["lat"][0], r["s0"]), locate(r["lon"][-1], r["lat"][-1], r["s1"])
    lo, hi = min(i0, i1), max(i0, i1); sl = pts[lo:hi + 1] if i0 <= i1 else pts[lo:hi + 1][::-1]
    out[rank] = {"state": r["state"], "node_ids": sl[:, 0].astype(int).tolist(), "node_lon": sl[:, 1].tolist(), "node_lat": sl[:, 2].tolist(),
                 "lon": r["lon"], "lat": r["lat"], "rank": rank, "road_key": r["road_key"], "highway": r["highway"]}
pickle.dump(out, open(D / "context/pilot_roads.pkl", "wb"))
rows = []
for st, pbf in (("VA", "data/raw/virginia-latest.osm.pbf"), ("MD", "data/raw/maryland-latest.osm.pbf")):
    names = [k for k, v in out.items() if v["state"] == st]
    if not names:
        continue
    tags, ways_ = read_context(pbf, set(i for k in names for i in out[k]["node_ids"]))
    for k in names:
        c = analyse(out[k], tags, ways_); g = rc.corner_and_lateral(out[k], c)
        try:
            t = rc.vdot(out[k], f"pilot{k}") if st == "VA" else rc.sha(out[k], f"pilot{k}")
        except Exception as e:
            t = {}
        rows.append({"rank": k, "road": out[k]["road_key"], "state": st, "km": round(c["length_km"], 1), "mph": c.get("speed_median_mph"), "signals": c["counts"]["signal"], "stops": c["counts"]["stop"],
                     "pub_junc": c["counts"]["pub_junction"], "driveways": c["counts"]["driveway"], "longest_clear_m": round(c["runs_hard_or_public_junction"]["longest_incl_ends_m"]),
                     "chain": g["longest_corner_chain"], "c30_km": round(g["corners_30deg_per_km"], 1), "gt0.5g": g.get("lat_share_gt0.5g"), "aadt": t.get("aadt_median"), "trucks%": t.get("trucks_pct"), "q": t.get("quality")})
pd.set_option("display.width", 250); print(pd.DataFrame(rows).round(2).to_string(index=False))
