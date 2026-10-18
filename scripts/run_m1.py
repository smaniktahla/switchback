"""M1: geometry metrics for every road in config/roads.yml, plus a sensitivity grid."""
import itertools
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, "src")
from switchback.geometry import Params, analyze, calibrate_radius, min_reliable_radius
from switchback.reference import load_roads

DER = Path("data/derived")


def load_line(rid):
    d = pd.read_csv(DER / rid / "centerline_nodes.csv")
    return d.lon.values, d.lat.values


def primary(rid, p):
    lon, lat = load_line(rid)
    ser, corners, straights, wins, road = analyze(lon, lat, p)
    out = DER / rid / "m1" / p.tag()
    out.mkdir(parents=True, exist_ok=True)
    ser.to_csv(out / "series.csv", index=False)
    corners.to_csv(out / "corners.csv", index=False)
    straights.to_csv(out / "straights.csv", index=False)
    for W, w in wins.items():
        w.to_csv(out / f"windows_{W}.csv", index=False)
    cal0 = calibrate_radius(p)
    cal1 = calibrate_radius(p, noise_m=1.0)
    road.update(params=p.__dict__ | {"angle_thrs": list(p.angle_thrs)},
                calibration_noise0={str(k): v for k, v in cal0.items()},
                calibration_noise1m={str(k): v for k, v in cal1.items()},
                min_reliable_radius_m=min_reliable_radius(cal0))
    (out / "road_summary.json").write_text(json.dumps(road, indent=1))
    return road


def sensitivity(rid, window_m=1000):
    lon, lat = load_line(rid)
    rows = []
    for ds, (sm, sg), rs in itertools.product(
            (5, 10, 20), (("none", 0), ("gaussian", 10), ("gaussian", 15), ("gaussian", 25), ("savgol", 60)),
            (300, 500, 1000)):
        p = Params(ds=ds, smooth=sm, sigma_m=sg, r_straight=rs)
        _, _, _, wins, road = analyze(lon, lat, p, window_sizes=(500, 1000, 2000))
        row = {"road_id": rid, "ds": ds, "smooth": sm, "sigma_m": sg, "r_straight": rs, **road}
        for W, w in wins.items():
            row[f"win{W}_deg_per_km_median"] = w.deg_per_km.median()
            row[f"win{W}_turns45_median"] = w.turns_per_km_45.median()
        rows.append(row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    base = Params()
    summ, sens = [], []
    for rid in load_roads():
        r = primary(rid, base)
        summ.append({"road_id": rid, **{k: v for k, v in r.items() if not isinstance(v, (dict, list))}})
        sens.append(sensitivity(rid))
    pd.DataFrame(summ).to_csv(DER / "m1_road_summary.csv", index=False)
    pd.concat(sens).to_csv(DER / "m1_sensitivity.csv", index=False)
    pd.set_option("display.width", 220, "display.max_columns", 50)
    print(pd.DataFrame(summ).set_index("road_id").T.round(2).to_string())
