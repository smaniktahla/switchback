"""Figures and summary tables for the US-211 climb sight-distance experiment."""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from switchback.sightdist import ssd_m

A, FIG = Path("data/derived/asd"), Path("reports/sightdist")
FIG.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
names = json.load(open(A / "run_meta.json"))["voxel_sets"]
DIRS = {"up_westbound": "Westbound (the climb)", "down_eastbound": "Eastbound (the descent)"}
STYLE = {"terrain": ("#888888", "--", "terrain only (upper bound)")}
for q, n in enumerate(names):
    STYLE[f"veg{q}"] = (["#1f77b4", "#08306b", "#6baed6"][q % 3], "-", f"terrain + lidar objects ({n})")


def prof(direction, pos="center"):
    return pd.read_csv(A / f"profile_{direction}_{pos}.csv")


def shade_corners(ax, ct):
    for _, c in ct.iterrows():
        ax.axvspan(c.s_entry, c.s_entry + c.length_m, color="#f4a261" if c["dir"] == "right" else "#8ecae6", alpha=.35, lw=0)


# A. profiles
for direction, title in DIRS.items():
    p, ct = prof(direction), pd.read_csv(A / f"corners_{direction}.csv")
    grade = np.gradient(p.road_z) / np.gradient(p.s_m)
    fig, ax = plt.subplots(2, 1, figsize=(12, 6.5), sharex=True)
    for a, comp, lab in ((ax[0], "path", "own lane pavement (hazard height 0.15 m)"), (ax[1], "opp", "oncoming vehicle in opposing lane (height 1.0 m)")):
        shade_corners(a, ct)
        for k, (col, ls, name) in STYLE.items():
            a.plot(p.s_m, p[f"{comp}_{k}"], color=col, ls=ls, lw=1.1, label=name)
        for mph in (35, 45):
            a.axhline(ssd_m(mph, float(-np.median(grade)) * 0), color="#b22222", lw=.8, ls=":")
            a.text(p.s_m.max() * .995, ssd_m(mph) + 3, f"AASHTO-style stopping distance @ {mph} mph (reference only)", ha="right", fontsize=7, color="#b22222")
        a.set_ylim(0, 260); a.set_ylabel("available sight distance (m)\n(capped at 250)"); a.set_title(lab, loc="left", fontsize=9)
    ax[0].legend(fontsize=7, loc="upper left", ncol=3)
    ax[1].set_xlabel("distance along the climb (m); shaded = corners >= 30 deg (blue left, orange right, in direction of travel)")
    fig.suptitle(f"US-211 climb, {title}: rider at lane centre (1.7 m from centreline), eye height 1.3 m", fontsize=10)
    fig.tight_layout(); fig.savefig(FIG / f"fig1_asd_profile_{direction}.png", dpi=130); plt.close(fig)

# B. per-corner
key = "path_veg0" if names else "path_terrain"; okey = key.replace("path", "opp")
fig, axes = plt.subplots(2, 1, figsize=(12, 7))
for a, (direction, title) in zip(axes, DIRS.items()):
    ct = pd.read_csv(A / f"corners_{direction}.csv"); x = np.arange(len(ct)); w = .27
    a.bar(x - w, ct[f"{key}_entry"], w, color="#9ecae1", label="own lane, at turn-in")
    a.bar(x, ct[f"{key}_apex"], w, color="#3182bd", label="own lane, at apex (distance visible beyond the apex)")
    a.bar(x + w, ct[f"{okey}_min"], w, color="#e6550d", label="opposing lane, worst point in corner")
    a.axhline(ssd_m(35), color="#b22222", ls=":", lw=.8); a.axhline(ssd_m(45), color="#b22222", ls=":", lw=.8)
    a.set_xticks(x); a.set_xticklabels([f"{r.corner}\n{r['dir'][0].upper()} {r.angle_deg}°\nR{r.min_radius_m}" for _, r in ct.iterrows()], fontsize=6.5)
    a.set_ylabel("sight distance (m)"); a.set_title(title + (" (with lidar objects)" if names else " (terrain only)"), loc="left", fontsize=9)
    a.set_ylim(0, 270)
axes[0].legend(fontsize=7, ncol=3, loc="upper left")
fig.tight_layout(); fig.savefig(FIG / "fig2_asd_per_corner.png", dpi=130); plt.close(fig)

# C. maps
fig, axs = plt.subplots(1, 2, figsize=(13, 4.5))
for a, (direction, title) in zip(axs, DIRS.items()):
    p = prof(direction); v = p[key if names else "path_terrain"]
    sc = a.scatter((p.x - p.x.min()) / 1000, (p.y - p.y.min()) / 1000, c=v, s=6, cmap="RdYlGn", vmin=40, vmax=250)
    a.set_aspect("equal"); a.set_title(f"{title}: own-lane sight distance", fontsize=9); a.set_xlabel("km"); a.set_ylabel("km")
fig.colorbar(sc, ax=axs, shrink=.8, label="sight distance (m)")
fig.savefig(FIG / "fig3_asd_map.png", dpi=130, bbox_inches="tight"); plt.close(fig)

# D. summary table
rows = []
for direction in DIRS:
    for pos in ("left", "center", "right"):
        p = prof(direction, pos); grade = np.gradient(p.road_z) / np.gradient(p.s_m)
        for k in ["terrain"] + [f"veg{q}" for q in range(len(names))]:
            r = {"direction": direction, "rider_position": pos, "variant": k if k == "terrain" else names[int(k[3:])]}
            for comp in ("path", "opp"):
                v = p[f"{comp}_{k}"]
                r.update({f"{comp}_median_m": round(float(v.median())), f"{comp}_p10_m": round(float(v.quantile(.1))),
                          f"{comp}_pct_ge_ssd35": round(100 * float((v >= np.array([ssd_m(35, g) for g in grade])).mean())),
                          f"{comp}_pct_ge_ssd45": round(100 * float((v >= np.array([ssd_m(45, g) for g in grade])).mean())),
                          f"{comp}_pct_capped": round(100 * float((v >= 249).mean())),
                          f"{comp}_pct_under_10m": round(100 * float((v < 10).mean()), 1)})
            rows.append(r)
s = pd.DataFrame(rows); s.to_csv(FIG / "summary.csv", index=False)
pd.set_option("display.width", 220); print(s.to_string(index=False))
