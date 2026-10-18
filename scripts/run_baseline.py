"""Ordinary-road baseline: measure 1 km windows on every other drivable road in the clipped regions,
then rank them by similarity to the reference roads (a preview of the later regional scan)."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from switchback.geometry import Params
from switchback.reference import load_roads
from switchback.scan import chain_ways, measure_chains, read_ways

DER, FIG = Path("data/derived"), Path("reports/figures")
P = Params()
REFS = ["us211_sperryville_thornton_gap", "us211_climb_km6_thornton_gap", "us129_dragon_deals_gap_tabcat",
        "us165_cherohala_skyway"]
FEATS = ["deg_per_km", "radius_p50", "turns_per_km_45", "frac_straight", "frac_R_lt_100", "straight_max_m"]


def ref_windows():
    out = []
    for rid in REFS:
        w = pd.read_csv(DER / rid / "m1" / P.tag() / "windows_1000.csv")
        w = w[~w.partial].copy(); w["road_key"] = rid; out.append(w)
    return pd.concat(out, ignore_index=True)


def embed(df, stats=None):
    x = pd.DataFrame({
        "deg_per_km": np.log10(df.deg_per_km.clip(lower=5)),
        "radius_p50": np.log10(df.radius_p50.fillna(2000).clip(upper=2000)),
        "turns_per_km_45": df.turns_per_km_45,
        "frac_straight": df.frac_straight,
        "frac_R_lt_100": df.frac_R_lt_100,
        "straight_max_m": np.log10(df.straight_max_m.fillna(0) + 10),
    })
    if stats is None:
        stats = (x.mean(), x.std().replace(0, 1))
    return ((x - stats[0]) / stats[1]), stats


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    exclude = set()
    for rid, cfg in load_roads().items():
        if "parent" not in cfg:
            exclude.update(json.load(open(DER / rid / "meta.json"))["ways_used"])
    ways = read_ways("data/gh/clip.osm.pbf", exclude_ids=exclude)
    chains = chain_ways(ways)
    base = measure_chains(chains, P)
    base["region"] = np.where(base.lon_mid < -83.0, "TN/NC", "VA")
    base.to_csv(DER / "baseline_windows_1000.csv", index=False)
    print(f"baseline: {len(ways)} ways -> {len(chains)} chains -> {len(base)} windows, "
          f"{base.road_key.nunique()} roads, {len(base)} km")
    refw = ref_windows()
    Eb, st = embed(base); Er, _ = embed(refw, st)
    # distance of every baseline window to its nearest reference window (any reference)
    d = np.sqrt(((Eb.values[:, None, :] - Er.values[None, :, :]) ** 2).sum(-1))
    base["nearest_ref_dist"] = d.min(1)
    base["nearest_ref"] = refw.road_key.values[d.argmin(1)]
    base.to_csv(DER / "baseline_windows_1000.csv", index=False)
    thr = np.percentile(base.nearest_ref_dist, 2)    # the most reference-like 2% of ordinary windows
    base["similar"] = base.nearest_ref_dist <= thr
    top = (base.groupby(["road_key", "region", "highway"]).agg(windows=("similar", "size"), similar=("similar", "sum"),
           med_deg_per_km=("deg_per_km", "median"), nearest=("nearest_ref", lambda s: s.mode().iat[0])).reset_index())
    top = top[top.similar > 0].sort_values(["similar", "windows"], ascending=False)
    top.to_csv(FIG / "scan_preview_top_roads.csv", index=False)
    print(top.head(15).to_string(index=False))
    # where do reference windows sit within the ordinary-road distribution?
    rows = []
    for rid in REFS:
        w = refw[refw.road_key == rid]
        rows.append({"road": rid, "windows": len(w),
                     "median_deg_per_km": w.deg_per_km.median(),
                     "pct_of_ordinary_below_median": float((base.deg_per_km < w.deg_per_km.median()).mean() * 100),
                     "median_turns45": w.turns_per_km_45.median(),
                     "pct_ordinary_below_turns45": float((base.turns_per_km_45 < w.turns_per_km_45.median()).mean() * 100)})
    pd.DataFrame(rows).to_csv(FIG / "reference_vs_ordinary.csv", index=False)
    print(pd.DataFrame(rows).round(1).to_string(index=False))
    byclass = base.groupby("highway").agg(windows=("deg_per_km", "size"), p50=("deg_per_km", "median"),
                                          p90=("deg_per_km", lambda s: s.quantile(.9)),
                                          p99=("deg_per_km", lambda s: s.quantile(.99)))
    byclass.to_csv(FIG / "baseline_by_class.csv"); print(byclass.round(0).to_string())


if __name__ == "__main__":
    main()
