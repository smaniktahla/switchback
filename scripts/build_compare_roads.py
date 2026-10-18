"""Pick the roads for the context comparison and attach their OSM node ids and fine geometry."""
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from switchback.scan import chain_ways

D = Path("data/derived")
ways, places = pickle.load(open(D / "scan_dc/region_ways.pkl", "rb"))
res, _, rng = pickle.load(open(D / "scan_dc/stretches_loose.pkl", "rb"))
ded = pd.read_csv(D / "scan_dc/all_deduped_stretches.csv")
chains = chain_ways(ways)
long_ = [c for c in chains if sum(a[0] for a in c["attrs"]) >= 3000.0]
stretch = {(r["chain_idx"], round(r["s0"], 1), round(r["s1"], 1)): r for r in res}

PICK = {  # label -> rank in reports/scan_dc/candidates.csv
    "Skyline Drive (cand. #1)": 1, "Lake Braddock Dr (cand. #11)": 11, "Park Central Rd MD (cand. #13)": 13,
    "Beach Drive MD (cand. #18)": 18, "US-211 east of New Market (cand. #19)": 19,
}
roads = {}
c = pd.read_csv(D / "../../data/derived/us211_climb_km6_thornton_gap/centerline_nodes.csv")
roads["US-211 climb (reference)"] = {"state": "VA", "node_ids": c.node_id.astype(int).tolist(), "node_lon": c.lon.tolist(),
                                    "node_lat": c.lat.tolist(), "lon": c.lon.tolist(), "lat": c.lat.tolist(), "rank": 0}
for label, rank in PICK.items():
    row = ded[ded["rank"] == rank].iloc[0]
    r = stretch[(int(row.chain_idx), round(row.s0, 1), round(row.s1, 1))]
    ch = long_[int(row.chain_idx)]
    pts = np.array([(p[0], p[1], p[2]) for p in ch["pts"]])
    raw = np.r_[0.0, np.cumsum([np.hypot((pts[i + 1, 1] - pts[i, 1]) * 86800, (pts[i + 1, 2] - pts[i, 2]) * 111200) for i in range(len(pts) - 1)])]
    def locate(lon, lat, s):          # nearest node to the stretch end that also lies near the expected distance along the chain
        win = np.abs(raw - s) <= max(0.06 * s, 250.0)
        d = np.hypot(pts[:, 1] - lon, pts[:, 2] - lat); d[~win] = 1e9
        return int(np.argmin(d))
    i0 = locate(r["lon"][0], r["lat"][0], r["s0"]); i1 = locate(r["lon"][-1], r["lat"][-1], r["s1"])
    lo, hi = min(i0, i1), max(i0, i1)
    sl = pts[lo:hi + 1] if i0 <= i1 else pts[lo:hi + 1][::-1]
    roads[label] = {"state": r["state"], "node_ids": sl[:, 0].astype(int).tolist(), "node_lon": sl[:, 1].tolist(),
                    "node_lat": sl[:, 2].tolist(), "lon": r["lon"], "lat": r["lat"], "rank": rank, "road_key": r["road_key"],
                    "highway": r["highway"], "way_ids": ch["way_ids"]}
    print(f"{label}: {r['road_key']} {r['state']} {len(sl)} nodes, stretch {row.length_m/1000:.1f} km, node path {(raw[hi]-raw[lo])/1000:.1f} km")
pickle.dump(roads, open(D / "context/roads.pkl", "wb"))
