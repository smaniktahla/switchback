"""Sight-distance experiment on the US-211 climb: ASD profiles, per-corner stats, both directions."""
import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from switchback.geometry import Params, build_series, segment
from switchback.sightdist import SightCfg, asd_components, ssd_m
from switchback.topography import DemSampler

ROAD = "us211_climb_km6_thornton_gap"
OUT = Path("data/derived/asd"); OUT.mkdir(parents=True, exist_ok=True)
P = Params()
OFFS = {"left": 0.85, "center": 1.70, "right": 2.55}
VOX_FILES = sorted(OUT.glob("voxels_*.npz"))       # produced by build_voxels.py when lidar is available


def load_vox():
    from switchback.lidar import Voxels
    out, names = [], []
    for f in VOX_FILES:
        z = np.load(f)
        v = Voxels.__new__(Voxels); v.o, v.vx, v.vz, v.keys = z["o"], float(z["vx"]), float(z["vz"]), z["keys"]
        out.append(v); names.append(f.stem.replace("voxels_", ""))
    return out, names


def corner_table(lon, lat, f, prof, z_path, names):
    ser = build_series(lon, lat, P)
    corners, _ = segment(ser, P)
    corners = corners[(~corners.partial) & (corners.angle_deg >= 30)].reset_index(drop=True)
    xy = np.c_[f["x"], f["y"]]
    def idx(s):
        k = int(np.argmin(np.abs(ser.s.values - s))); return int(np.argmin(np.hypot(xy[:, 0] - ser.x.values[k], xy[:, 1] - ser.y.values[k])))
    grade = np.gradient(z_path) / np.gradient(f["s"])
    rows = []
    for ci, c in corners.iterrows():
        a, e = idx(c.s_start), idx(c.s_end)
        if e <= a:
            continue
        seg = ser[(ser.s >= c.s_start) & (ser.s <= c.s_end)]
        apex = idx(float(seg.s.values[int(np.argmax(np.abs(seg.kappa.values)))]))
        r = {"corner": ci + 1, "dir": "left" if c.sign > 0 else "right", "angle_deg": round(c.angle_deg),
             "min_radius_m": round(c.min_radius_m), "s_entry": round(f["s"][a]), "length_m": round(f["s"][e] - f["s"][a]),
             "grade_pct": round(100 * float(np.mean(grade[a:e + 1])), 1)}
        for key in ["path_terrain", "opp_terrain"] + [f"{p}_veg{q}" for q in range(len(names)) for p in ("path", "opp")]:
            v = prof[key]
            r[f"{key}_entry"] = round(float(v[a])); r[f"{key}_apex"] = round(float(v[apex])); r[f"{key}_min"] = round(float(v[a:e + 1].min()))
        for key in ["path_terrain"] + [f"path_veg{q}" for q in range(len(names))]:
            v = prof[key]
            r[f"{key}_sees_exit_from_entry"] = bool(v[a] >= f["s"][e] - f["s"][a])
            r[f"{key}_sees_exit_from_apex"] = bool(v[apex] >= f["s"][e] - f["s"][apex])
            r[f"{key}_beyond_exit_from_apex_m"] = round(float(v[apex] - (f["s"][e] - f["s"][apex])))
        r["ssd_35mph_m"] = round(ssd_m(35, float(np.mean(grade[a:e + 1])))); r["ssd_45mph_m"] = round(ssd_m(45, float(np.mean(grade[a:e + 1]))))
        rows.append(r)
    return pd.DataFrame(rows)


def main():
    d = pd.read_csv(f"data/derived/{ROAD}/centerline_nodes.csv")
    vox, names = load_vox()
    print("voxel sets:", names, flush=True)
    results = {}
    for direction, (lon, lat) in {"up_westbound": (d.lon.values, d.lat.values), "down_eastbound": (d.lon.values[::-1], d.lat.values[::-1])}.items():
        for pos, off in OFFS.items():
            if pos != "center" and names:      # lane-position sensitivity on terrain only plus the headline voxel run
                pass
            cfg = replace(SightCfg(), rider_off=off)
            from pyproj import Transformer
            ep = 32617
            smp = DemSampler(Path("data/dem") / f"{ROAD}_1m", 1, ep)
            ground = lambda x, y: smp.sample(x, y)
            f, prof, z_path = asd_components(lon, lat, ground, vox, cfg)
            df = pd.DataFrame({"s_m": f["s"], "x": f["x"], "y": f["y"], "road_z": z_path, **prof})
            df.to_csv(OUT / f"profile_{direction}_{pos}.csv", index=False)
            results[(direction, pos)] = (f, prof, z_path)
            print(direction, pos, "done; median path ASD terrain %.0f m" % np.median(prof["path_terrain"]), flush=True)
            if pos == "center":
                ct = corner_table(lon, lat, f, prof, z_path, names)
                ct.to_csv(OUT / f"corners_{direction}.csv", index=False)
                print(ct[["corner", "dir", "angle_deg", "min_radius_m", "path_terrain_entry", "path_terrain_apex", "path_terrain_min", "opp_terrain_apex"]].to_string(index=False), flush=True)
    json.dump({"voxel_sets": names}, open(OUT / "run_meta.json", "w"))


if __name__ == "__main__":
    main()
