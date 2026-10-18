"""Above-ground lidar obstruction voxels along the US-211 climb from the 2014 NRCS Shenandoah point cloud."""
import sys
from pathlib import Path

import laspy
import numpy as np
import pandas as pd
from pyproj import CRS, Transformer
from scipy.spatial import cKDTree

sys.path.insert(0, "src")
from switchback.geometry import project, resample
from switchback.lidar import Voxels
from switchback.topography import DemSampler

ROAD, BUFFER_M, EPSG = "us211_climb_km6_thornton_gap", 150.0, 32617
TILES = sorted(Path("data/lidar/NRCS_Shenandoah_2014").glob("USGS_*.laz"))
OUT = Path("data/derived/asd")
EXCLUDE = {2, 7, 9, 13, 14, 15, 16, 18}         # ground, noise, water, wires/towers
VX, VZ = 1.0, 0.5


def main():
    d = pd.read_csv(f"data/derived/{ROAD}/centerline_nodes.csv")
    x, y, _ = project(d.lon.values, d.lat.values)
    cx, cy, _ = resample(x, y, 5.0)
    tree = cKDTree(np.c_[cx, cy])
    org = np.array([cx.min() - BUFFER_M - 10, cy.min() - BUFFER_M - 10, 0.0])
    smp = DemSampler(Path("data/dem") / f"{ROAD}_1m", 1, EPSG)
    keyer = Voxels(np.array([[org[0], org[1], 0.0]]), org, VX, VZ)      # only used for its key function
    keys, stats = [], {"read": 0, "kept": 0}
    classes, gps = {}, []
    for t in TILES:
        with laspy.open(t) as rd:
            crs = CRS.from_epsg(6593)        # tiles lack a CRS: header GeoKeys say NAD83(2011) / Virginia North (ftUS)
            vunit = "US survey foot"
            zscale = 0.3048006096             # NAVD88 height in US survey feet -> metres
            tr = Transformer.from_crs(crs, EPSG, always_xy=True)
            print(t.name, "crs:", crs.name if crs else None, "| vertical unit:", vunit, "| zscale", zscale, "| points", rd.header.point_count, flush=True)
            for chunk in rd.chunk_iterator(4_000_000):
                px, py = np.asarray(chunk.x), np.asarray(chunk.y)
                if tr is not None:
                    px, py = tr.transform(px, py)
                # cheap bbox pre-filter before the KD-tree query
                m = (px >= org[0]) & (py >= org[1]) & (px <= cx.max() + BUFFER_M + 10) & (py <= cy.max() + BUFFER_M + 10)
                if not m.any():
                    continue
                dist, _ = tree.query(np.c_[px[m], py[m]], distance_upper_bound=BUFFER_M)
                sel = np.flatnonzero(m)[np.isfinite(dist)]
                if not len(sel):
                    continue
                cls = np.asarray(chunk.classification)[sel]
                for c, n in zip(*np.unique(cls, return_counts=True)):
                    classes[int(c)] = classes.get(int(c), 0) + int(n)
                stats["read"] += len(sel)
                keep = ~np.isin(cls, list(EXCLUDE))
                px_, py_, pz_ = px[sel][keep], py[sel][keep], np.asarray(chunk.z)[sel][keep] * zscale
                g = smp.sample(px_, py_)
                above = np.isfinite(g) & (pz_ - g >= 0.3)       # drop road-surface / ground-noise returns
                gps.append(np.asarray(chunk.gps_time)[sel][keep][above][:1000])
                keys.append(keyer._key(px_[above], py_[above], pz_[above]) if above.any() else np.empty(0, np.int64))
                stats["kept"] += int(above.sum())
        print("  cumulative corridor points:", stats["read"], "non-ground kept:", stats["kept"], flush=True)
    allk = np.concatenate(keys)
    u, cnt = np.unique(allk, return_counts=True)
    print("classes in corridor:", classes)
    print("voxels: any>=1:", len(u), " >=2 pts:", int((cnt >= 2).sum()), " >=3 pts:", int((cnt >= 3).sum()))
    area_km2 = len(cx) * 5.0 * 2 * BUFFER_M / 1e6
    print("approx corridor area km2 %.2f -> %.1f non-ground pts per m2" % (area_km2, stats["kept"] / (area_km2 * 1e6)))
    for name, k in (("any", u), ("dense", u[cnt >= 2])):
        np.savez(OUT / f"voxels_{name}.npz", o=org, vx=VX, vz=VZ, keys=k)
    g = np.concatenate(gps) if gps else np.array([0.0])
    import datetime as dt
    print("gps_time raw range:", float(g.min()), float(g.max()))
    for off in (1e9, 0):
        try:
            print(f"  as GPS seconds (+{off:.0e}):", (dt.datetime(1980, 1, 6) + dt.timedelta(seconds=float(np.median(g)) + off)).date())
        except OverflowError:
            pass


if __name__ == "__main__":
    main()
