"""Rank, de-duplicate and describe the scan_region stretches: places, elevation, links, GPX, map."""
import json
import math
import pickle
import sys
from pathlib import Path
from urllib.parse import quote

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

sys.path.insert(0, "src")
from switchback.geometry import Params, build_series
from switchback.topography import DemSampler, add_topography, sample_profile, topo_features

DC, TOPN = (38.9072, -77.0369), 40
OUT, REP = Path("data/derived/scan_dc"), Path("reports/scan_dc")
P = Params()
COMPASS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def km_xy(lon, lat):
    return (np.asarray(lon) - DC[1]) * 111.32 * math.cos(math.radians(DC[0])), (np.asarray(lat) - DC[0]) * 110.57


def bearing(dx, dy):
    return COMPASS[int(((math.degrees(math.atan2(dx, dy)) + 360) % 360 + 22.5) // 45) % 8]


def hav_km(lon1, lat1, lon2, lat2):
    x, y = km_xy(lon2, lat2); x0, y0 = km_xy(lon1, lat1)
    return float(np.hypot(x - x0, y - y0))


def main():
    res, places, rng = pickle.load(open(OUT / "stretches_loose.pkl", "rb"))
    df = pd.DataFrame(res)
    df["mid_lon"] = [l[len(l) // 2] for l in df.lon]; df["mid_lat"] = [l[len(l) // 2] for l in df.lat]
    df = df.sort_values("score").reset_index(drop=True)
    keep = []
    for i, r in df.iterrows():
        ok = True
        for j in keep:
            k = df.loc[j]
            if hav_km(r.mid_lon, r.mid_lat, k.mid_lon, k.mid_lat) < 1.5:
                ok = False; break
            if r.chain_idx == k.chain_idx:
                ov = min(r.s1, k.s1) - max(r.s0, k.s0)
                if ov > 0.3 * min(r.length_m, k.length_m):
                    ok = False; break
        if ok:
            keep.append(i)
    ded = df.loc[keep].reset_index(drop=True)
    ded["rank"] = ded.index + 1
    # reference check: where does the US-211 climb itself land?
    ref = pd.read_csv("data/derived/us211_climb_km6_thornton_gap/centerline_nodes.csv")
    rmid = ref.iloc[len(ref) // 2]
    ded["dist_to_us211_ref_km"] = [hav_km(rmid.lon, rmid.lat, a, b) for a, b in zip(ded.mid_lon, ded.mid_lat)]
    ref_rank = ded[ded.dist_to_us211_ref_km < 3.0]["rank"].tolist()
    # places and distance from DC
    pl = pd.DataFrame(places, columns=["name", "lon", "lat", "cls"]).drop_duplicates(["name", "lon", "lat"])
    sig = pl[pl.cls.isin(["city", "town", "village"])]
    t_sig = cKDTree(np.c_[km_xy(sig.lon, sig.lat)]); t_all = cKDTree(np.c_[km_xy(pl.lon, pl.lat)])
    near, dcs = [], []
    for _, r in ded.iterrows():
        x, y = km_xy(r.mid_lon, r.mid_lat)
        d, i = t_sig.query([x, y])
        row = sig.iloc[i] if d <= 12 else pl.iloc[t_all.query([x, y])[1]]
        px, py = km_xy(row.lon, row.lat); d = float(np.hypot(x - px, y - py))
        near.append(f"{d:.0f} km {bearing(x - px, y - py)} of {row['name']}" if d >= 1.5 else f"at {row['name']}")
        dcs.append(f"{np.hypot(x, y):.0f} km {bearing(x, y)}")
    ded["where"], ded["from_dc"] = near, dcs
    # elevation for the top N (10 m 3DEP, distance-smoothed; bridges not masked)
    top = ded.head(TOPN).copy()
    topo = []
    for _, r in top.iterrows():
        ser = build_series(r.lon, r.lat, P)
        smp = DemSampler(Path("data/dem") / f"scan_{ser.attrs['epsg']}_10m", 10, ser.attrs["epsg"])
        ser = add_topography(ser, sample_profile(ser, smp, 0.0), 20)
        v = ser.s[ser.valid]
        topo.append(topo_features(ser, float(v.min()), float(v.max()) + 1e-6))
    t = pd.DataFrame(topo)
    for c in ["gain_m", "loss_m", "net_m", "mean_abs_grade_pct", "max_sustained_grade_250m_pct"]:
        top[c] = t[c].values
    # links, gpx, outputs
    def links(r):
        lon, lat = r.lon, r.lat
        n = len(lon); k = min(8, max(1, int(r.length_m / 1000)))
        idx = np.linspace(0, n - 1, k + 2).round().astype(int)[1:-1]
        wp = quote("|".join(f"{lat[i]},{lon[i]}" for i in idx), safe=",")
        g = (f"https://www.google.com/maps/dir/?api=1&origin={lat[0]},{lon[0]}&destination={lat[-1]},{lon[-1]}"
             f"&waypoints={wp}&travelmode=driving")
        o = f"https://www.openstreetmap.org/?mlat={r.mid_lat}&mlon={r.mid_lon}#map=13/{r.mid_lat}/{r.mid_lon}"
        return g, o
    top[["gmaps", "osm"]] = [links(r) for _, r in top.iterrows()]
    top["fit"] = (100 * (1 - top.score)).clip(lower=0).round(0)
    cols = ["rank", "road_key", "highway", "state", "where", "from_dc", "length_m", "score", "fit", "match_share", "deg_per_km",
            "turns_per_km_45", "radius_p50", "frac_straight", "frac_R_lt_50", "gain_m", "loss_m", "net_m",
            "mean_abs_grade_pct", "max_sustained_grade_250m_pct", "mid_lat", "mid_lon", "gmaps", "osm"]
    top[cols].to_csv(REP / "candidates.csv", index=False)
    ded[[c for c in ded.columns if c not in ("lon", "lat")]].to_csv(OUT / "all_deduped_stretches.csv", index=False)
    with open(REP / "candidates.gpx", "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.1" creator="switchback" xmlns="http://www.topografix.com/GPX/1/1">\n')
        for _, r in top.iterrows():
            f.write(f"<trk><name>#{r['rank']} {r.road_key} ({r.state}) {r.length_m/1000:.1f} km</name><trkseg>\n")
            for a, b in list(zip(r.lon, r.lat))[::3]:
                f.write(f'<trkpt lat="{b}" lon="{a}"/>\n')
            f.write("</trkseg></trk>\n")
        f.write("</gpx>\n")
    # markdown
    L = ["# US-211-like stretches within ~2 h of DC (VA, MD, WV)", "",
         f"Template: the US-211 climb (Sperryville to Thornton Gap), 4.8 km. A stretch is 3-10 km of paved public road whose 1 km windows all sit "
         f"inside the climb's own range (+/-25%): heading change {rng['strict']['deg_per_km'][0]:.0f}-{rng['strict']['deg_per_km'][1]:.0f} deg/km, median radius "
         f"{rng['strict']['radius_p50'][0]:.0f}-{rng['strict']['radius_p50'][1]:.0f} m, {rng['strict']['turns_per_km_45'][0]:.1f}-{rng['strict']['turns_per_km_45'][1]:.1f} turns >= 45 deg/km, "
         f"{100*rng['strict']['frac_straight'][0]:.0f}-{100*rng['strict']['frac_straight'][1]:.0f}% straight. Ranked by closeness to the centre of that range (fit 100 = dead centre, 0 = edge).", "",
         "| # | Road | Where | Len km | Fit | Turns>=45/km | Radius m | Straight | Up/Down m | Grade | From DC | Map |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in top.iterrows():
        L.append(f"| {r['rank']} | {r.road_key} ({r.highway}) | {r.state}, {r.where} | {r.length_m/1000:.1f} | {r.fit:.0f} | {r.turns_per_km_45:.1f} | "
                 f"{r.radius_p50:.0f} | {100*r.frac_straight:.0f}% | +{r.gain_m:.0f}/-{r.loss_m:.0f} | {r.mean_abs_grade_pct:.1f}% | {r.from_dc} | "
                 f"[Google]({r.gmaps}) / [OSM]({r.osm}) |")
    (REP / "candidates.md").write_text("\n".join(L) + "\n")
    # overview map
    fig, ax = plt.subplots(figsize=(9, 8))
    for _, r in ded.iterrows():
        x, y = km_xy(r.lon, r.lat); ax.plot(x, y, color="#cccccc", lw=.6)
    for _, r in top.iterrows():
        x, y = km_xy(r.lon, r.lat); ax.plot(x, y, lw=1.6, color="#d62728" if r["rank"] <= 10 else "#1f77b4")
        ax.text(x[len(x) // 2], y[len(y) // 2], str(r["rank"]), fontsize=6, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=.8))
    ax.plot(0, 0, "k*", ms=12); ax.text(2, 2, "DC", fontsize=9)
    ax.set_aspect("equal"); ax.set_xlabel("km east of DC"); ax.set_ylabel("km north of DC")
    ax.set_title(f"US-211-like stretches near DC: top {TOPN} numbered (top 10 red), all {len(ded)} grey")
    fig.tight_layout(); fig.savefig(REP / "overview.png", dpi=130)
    summ = {"raw_stretches": len(df), "after_dedup": len(ded), "top_n": TOPN, "us211_reference_ranks": ref_rank,
            "by_state_top40": top.state.value_counts().to_dict(), "by_state_all": ded.state.value_counts().to_dict(),
            "length_km_median_top40": float(top.length_m.median() / 1000)}
    (REP / "summary.json").write_text(json.dumps(summ, indent=1)); print(json.dumps(summ, indent=1))
    pd.set_option("display.width", 250, "display.max_colwidth", 60)
    print(top[["rank", "road_key", "state", "where", "length_m", "fit", "turns_per_km_45", "radius_p50", "gain_m", "loss_m", "mean_abs_grade_pct"]].round(1).head(25).to_string(index=False))


if __name__ == "__main__":
    main()
