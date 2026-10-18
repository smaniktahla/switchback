"""M2a: elevation (USGS 3DEP) topography metrics, DEM-resolution / smoothing / lateral sensitivity."""
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from switchback.geometry import Params, analyze, build_series, segment
from switchback.reference import load_roads
from switchback.topography import DemSampler, add_topography, deck_interpolate, sample_profile, topo_features

DER, DEMDIR = Path("data/derived"), Path("data/dem")
P = Params()
PRIMARY = dict(res=1, sigma_e=20, lateral=0)


def main():
    rows_sens, summ = [], []
    for rid in load_roads():
        d = pd.read_csv(DER / rid / "centerline_nodes.csv")
        ser0 = build_series(d.lon.values, d.lat.values, P)
        epsg = ser0.attrs["epsg"]
        profiles = {}
        for res in ((1, 10) if ser0.attrs["raw_len"] > 30000 else (1, 10, 30)):   # skip 30 m on very long roads
            smp = DemSampler(DEMDIR / f"{rid}_{res}m", res, epsg)
            for lat_m in (0, 6):
                profiles[(res, lat_m)] = sample_profile(ser0, smp, lat_m)
        deck = np.interp(ser0.s_raw.values, d.cum_m.values * ser0.s_raw.values[-1] / d.cum_m.values[-1],
                         d.deck.values.astype(float)) > 0.5 if "deck" in d else np.zeros(len(ser0), bool)
        profiles = {k: deck_interpolate(v_, deck) for k, v_ in profiles.items()}
        v = ser0.valid.values
        lo, hi = float(ser0.s[v].min()), float(ser0.s[v].max()) + 1e-6
        for (res, lat_m), prof in profiles.items():
            for sg in (0, 10, 20, 40):
                ser = add_topography(ser0, prof, sg)
                f = topo_features(ser, lo, hi)
                rows_sens.append({"road_id": rid, "dem_res_m": res, "lateral_m": lat_m, "sigma_e_m": sg, **f})
        # primary outputs
        prof = profiles[(PRIMARY["res"], PRIMARY["lateral"])]
        ser = add_topography(ser0, prof, PRIMARY["sigma_e"])
        corners, straights = segment(ser, P)
        road = topo_features(ser, lo, hi)
        ak, ag = np.abs(ser.kappa.values[v]), np.abs(ser.grade.values[v])
        curved = ak > 1 / P.r_straight
        road["mean_abs_grade_in_curves_pct"] = float(100 * ag[curved].mean())
        road["mean_abs_grade_on_straights_pct"] = float(100 * ag[~curved].mean())
        road["dem_nan_samples"] = int(np.isnan(prof).sum())
        road["deck_share_interpolated"] = float(deck[v].mean())
        out = DER / rid / "m2"
        out.mkdir(parents=True, exist_ok=True)
        ser[["s", "s_raw", "lon", "lat", "ele_raw", "ele", "grade", "kappa", "valid"]].to_csv(out / "profile.csv", index=False)
        # windows: M1 geometry features + topography
        m1 = DER / rid / "m1" / P.tag()
        for W in (500, 1000, 2000):
            w = pd.read_csv(m1 / f"windows_{W}.csv")
            tf = pd.DataFrame([topo_features(ser, a, b) for a, b in zip(w.s0, w.s1)])
            pd.concat([w, tf], axis=1).to_csv(out / f"windows_{W}_topo.csv", index=False)
        road["params"] = PRIMARY | {"dem": "USGS 3DEP via ImageServer exportImage, bilinear", "geometry_params": P.tag()}
        (out / "topo_summary.json").write_text(json.dumps(road, indent=1))
        summ.append({"road_id": rid, **{k: v for k, v in road.items() if not isinstance(v, dict)}})
    pd.DataFrame(rows_sens).to_csv(DER / "m2_topo_sensitivity.csv", index=False)
    pd.DataFrame(summ).to_csv(DER / "m2_topo_summary.csv", index=False)
    pd.set_option("display.width", 220)
    print(pd.DataFrame(summ).set_index("road_id").T.round(2).to_string())


if __name__ == "__main__":
    main()
