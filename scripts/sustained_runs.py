"""How long do roads stay twisty? Longest run of consecutive 1 km windows above a heading-change threshold."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, "src")
from switchback.geometry import Params
from switchback.scan import longest_runs

DER, FIG, P = Path("data/derived"), Path("reports/figures"), Params()
REFS = ["us211_sperryville_thornton_gap", "us211_climb_km6_thornton_gap", "us129_dragon_deals_gap_tabcat", "us165_cherohala_skyway"]
base = pd.read_csv(DER / "baseline_windows_1000.csv")
refw = pd.concat([pd.read_csv(DER / r / "m1" / P.tag() / "windows_1000.csv").assign(road_key=r) for r in REFS])
refw = refw[~refw.partial]
out = []
for thr in (150, 250):
    rr = longest_runs(refw, "road_key", thr); rr["thr"] = thr; rr["kind"] = "reference"; out.append(rr.rename(columns={"road_key": "road"}))
    b = longest_runs(base.assign(c=base.road_key + "|" + base.chain_idx.astype(str)), "c", thr)
    meta = base.groupby(base.road_key + "|" + base.chain_idx.astype(str)).agg(highway=("highway", "first"), region=("region", "first"),
                                                                       chain_km=("chain_km", "first"), unpaved=("chain_unpaved_share", "first"),
                                                                       surf_tagged=("chain_surface_tagged", "first"))
    b = b.merge(meta, left_on="c", right_index=True); b["road"] = b.c.str.split("|").str[0]; b["thr"] = thr; b["kind"] = "ordinary"
    out.append(b.drop(columns="c"))
res = pd.concat(out); res.to_csv(FIG / "sustained_runs.csv", index=False)
for thr in (150, 250):
    r = res[(res.thr == thr) & (res.kind == "reference")]
    print(f"\nreference roads, longest run >= {thr} deg/km (km):"); print(r[["road", "longest_run_windows", "windows", "share_above"]].round(2).to_string(index=False))
    o = res[(res.thr == thr) & (res.kind == "ordinary")].sort_values("longest_run_windows", ascending=False).head(12)
    print(f"ordinary roads: top 12 by longest run >= {thr} deg/km:"); print(o[["road", "region", "highway", "chain_km", "longest_run_windows", "share_above", "unpaved", "surf_tagged"]].round(2).to_string(index=False))
    o = res[(res.thr == thr) & (res.kind == "ordinary")]
    print("ordinary chains with a run >= 4 km:", int((o.longest_run_windows >= 4).sum()), "of", len(o))
