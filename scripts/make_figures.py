"""Figures and comparison tables for the reference roads (reads data/derived, writes reports/figures)."""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from switchback.geometry import Params

DER, FIG = Path("data/derived"), Path("reports/figures")
FIG.mkdir(parents=True, exist_ok=True)
P = Params()
ROADS = {"us211_sperryville_thornton_gap": ("US-211 Sperryville-Thornton Gap", "#1f77b4"),
         "us129_dragon_deals_gap_tabcat": ("US-129 Tail of the Dragon", "#d62728"),
         "us165_cherohala_skyway": ("Cherohala Skyway", "#2ca02c")}
CLIMB = "us211_climb_km6_thornton_gap"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def series(rid):
    s = pd.read_csv(DER / rid / "m2" / "profile.csv")
    m1 = pd.read_csv(DER / rid / "m1" / P.tag() / "series.csv")
    s["x"], s["y"] = m1.x, m1.y
    return s[s.valid]


def radius(s):
    k = s.kappa.abs()
    return (1 / k[k > 1 / P.r_straight])


S = {rid: series(rid) for rid in list(ROADS) + [CLIMB]}
base = pd.read_csv(DER / "baseline_windows_1000.csv") if (DER / "baseline_windows_1000.csv").exists() else None

# 1. signed curvature vs distance
fig, ax = plt.subplots(3, 1, figsize=(11, 7.5))
for a, (rid, (name, c)) in zip(ax, ROADS.items()):
    s = S[rid]
    a.plot(s.s / 1000, 1000 * s.kappa, lw=0.5, color=c)
    a.axhline(0, c="k", lw=0.3); a.set_ylim(-80, 80); a.set_ylabel("curvature (1/km)\nleft +")
    a.set_title(f"{name}  ({s.s.max()/1000:.1f} km)", loc="left", fontsize=9)
    if rid.startswith("us211"):
        a.axvline(6.0, color="k", ls=":", lw=0.8); a.text(6.05, 62, "climb sub-segment starts", fontsize=8)
ax[-1].set_xlabel("distance along road (km)")
fig.tight_layout(); fig.savefig(FIG / "fig1_curvature_vs_distance.png", dpi=130); plt.close(fig)

# 2. radius vs distance + radius histogram (length-weighted share)
fig, ax = plt.subplots(3, 2, figsize=(11, 7.5), gridspec_kw={"width_ratios": [3, 1.3]})
bins = np.logspace(np.log10(15), np.log10(500), 30)
for i, (rid, (name, c)) in enumerate(ROADS.items()):
    s = S[rid]; k = s.kappa.abs(); m = k > 1 / P.r_straight
    ax[i, 0].scatter(s.s[m] / 1000, 1 / k[m], s=1.5, color=c, alpha=.5); ax[i, 0].set_yscale("log")
    ax[i, 0].set_ylim(15, 500); ax[i, 0].set_ylabel("curve radius (m)"); ax[i, 0].set_title(name, loc="left", fontsize=9)
    ax[i, 0].axhline(P.r_straight, color="k", lw=.3)
    r = radius(s)
    ax[i, 1].hist(r, bins=bins, weights=np.full(len(r), 100 / len(s)), color=c); ax[i, 1].set_xscale("log")
    ax[i, 1].set_ylabel("% of road length")
    ax[i, 1].text(.97, .9, f"median {r.median():.0f} m\n{(s.kappa.abs() < 1/P.r_straight).mean()*100:.0f}% straight (R>500)",
                  transform=ax[i, 1].transAxes, ha="right", va="top", fontsize=8)
ax[-1, 0].set_xlabel("distance along road (km)"); ax[-1, 1].set_xlabel("radius (m)")
fig.tight_layout(); fig.savefig(FIG / "fig2_curve_radius.png", dpi=130); plt.close(fig)

# 3. elevation profiles with grade
fig, ax = plt.subplots(3, 1, figsize=(11, 7.5))
for a, (rid, (name, c)) in zip(ax, ROADS.items()):
    s = S[rid]
    a.plot(s.s_raw / 1000, s.ele, color=c); a.set_ylabel("elevation (m)")
    b = a.twinx(); b.plot(s.s_raw / 1000, 100 * pd.Series(s.grade.values).rolling(25, center=True, min_periods=1).mean(),
                          color="grey", lw=.5, alpha=.7); b.set_ylabel("grade % (250 m avg)"); b.set_ylim(-14, 14)
    b.spines["right"].set_visible(True)
    t = json.load(open(DER / rid / "m2" / "topo_summary.json"))
    a.set_title(f"{name}: +{t['gain_m']:.0f} m / -{t['loss_m']:.0f} m, mean |grade| {t['mean_abs_grade_pct']:.1f}%, "
                f"max sustained 250 m {t['max_sustained_grade_250m_pct']:.1f}%", loc="left", fontsize=9)
ax[-1].set_xlabel("distance along road (km)")
fig.tight_layout(); fig.savefig(FIG / "fig3_elevation_profile.png", dpi=130); plt.close(fig)

# 4. feature distributions per 1 km window: ordinary roads vs references
feats = [("deg_per_km", "heading change (deg/km)", True), ("turns_per_km_45", "turns >= 45 deg per km", False),
         ("radius_p50", "median curve radius (m)", True), ("frac_straight", "share of length straight (R>500)", False),
         ("straight_max_m", "longest straight in window (m)", False)]
groups = [("ordinary\nroads", base)] if base is not None else []
wins = {rid: pd.read_csv(DER / rid / "m1" / P.tag() / "windows_1000.csv") for rid in list(ROADS) + [CLIMB]}
wins = {k: v[~v.partial] for k, v in wins.items()}
groups += [("US-211\nfull", wins["us211_sperryville_thornton_gap"]), ("US-211\nclimb", wins[CLIMB]),
           ("Dragon", wins["us129_dragon_deals_gap_tabcat"]), ("Cherohala", wins["us165_cherohala_skyway"])]
cols = ["#bbbbbb", "#1f77b4", "#6baed6", "#d62728", "#2ca02c"][:len(groups)] if base is not None else ["#1f77b4", "#6baed6", "#d62728", "#2ca02c"]
fig, ax = plt.subplots(1, len(feats), figsize=(14, 3.8))
for a, (f, lab, lg) in zip(ax, feats):
    data = [g[f].dropna().values for _, g in groups]
    bp = a.boxplot(data, patch_artist=True, showfliers=False, widths=.6, whis=(5, 95))
    for patch, c in zip(bp["boxes"], cols):
        patch.set_facecolor(c); patch.set_alpha(.8)
    a.set_xticks(range(1, len(groups) + 1)); a.set_xticklabels([g[0] for g in groups], fontsize=7)
    a.set_title(lab, fontsize=8)
    if lg:
        a.set_yscale("log")
fig.suptitle("1 km windows: boxes = 25-75%, whiskers = 5-95%" + (f"  (ordinary roads: {len(base)} windows)" if base is not None else ""), fontsize=9)
fig.tight_layout(); fig.savefig(FIG / "fig4_feature_distributions.png", dpi=130); plt.close(fig)

# 5. maps along the real geometry, coloured by local curve tightness
fig, ax = plt.subplots(1, 3, figsize=(14, 5))
for a, (rid, (name, c)) in zip(ax, ROADS.items()):
    s = S[rid]; tight = (1000 * s.kappa.abs()).rolling(15, center=True, min_periods=1).mean().clip(upper=50)
    sc = a.scatter((s.x - s.x.min()) / 1000, (s.y - s.y.min()) / 1000, c=tight, s=2, cmap="magma_r", vmin=0, vmax=50)
    a.set_aspect("equal"); a.set_title(name, fontsize=9); a.set_xlabel("km"); a.set_ylabel("km")
fig.colorbar(sc, ax=ax, shrink=.7, label="curve tightness (1/km, 150 m avg)")
fig.savefig(FIG / "fig5_maps_curve_tightness.png", dpi=130, bbox_inches="tight"); plt.close(fig)

# 6. GraphHopper curvature levels per road (length-weighted)
gp = DER / "gh_crosscheck" / "summary.json"
if gp.exists():
    g = json.load(open(gp)); fig, ax = plt.subplots(figsize=(9, 3 + .5 * len(g)))
    levels = sorted({lv for v in g.values() for lv in v["gh_value_levels_length_weighted"]}, key=float)
    cm = plt.cm.RdYlGn(np.linspace(0.05, .95, len(levels)))
    for i, (rid, v) in enumerate(g.items()):
        left = 0
        for lv, c in zip(levels, cm):
            w = v["gh_value_levels_length_weighted"].get(lv, 0) * 100
            ax.barh(i, w, left=left, color=c, edgecolor="white", label=lv if i == 0 else None); left += w
        ax.text(101, i, f"{v['n_edges']} edges, median {v['median_edge_length_m']:.0f} m, max {v['max_edge_length_m']:.0f} m",
                va="center", fontsize=8)
    ax.set_yticks(range(len(g))); ax.set_yticklabels([ROADS[r][0] for r in g], fontsize=8)
    ax.set_xlim(0, 100); ax.set_xlabel("% of road length at each GraphHopper curvature value (0.25 = tightest, 1.0 = straight)")
    ax.legend(ncol=len(levels), fontsize=6, loc="upper center", bbox_to_anchor=(.5, -.25), title="GH curvature value", title_fontsize=7)
    fig.subplots_adjust(right=.62); fig.savefig(FIG / "fig6_graphhopper_curvature.png", dpi=130, bbox_inches="tight"); plt.close(fig)

# 7. scan preview: ordinary windows vs reference windows in feature space
if base is not None:
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(base.deg_per_km, base.radius_p50, s=4, color="#cccccc", label="ordinary roads (1 km windows)")
    for rid, (name, c) in ROADS.items():
        w = wins[rid]; ax.scatter(w.deg_per_km, w.radius_p50, s=14, color=c, label=name)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("heading change (deg/km)"); ax.set_ylabel("median curve radius (m)")
    ax.legend(fontsize=7); fig.tight_layout(); fig.savefig(FIG / "fig7_reference_vs_ordinary.png", dpi=130); plt.close(fig)

# comparison table
rows = []
for rid in list(ROADS) + [CLIMB]:
    s = S[rid]; r1 = json.load(open(DER / rid / "m1" / P.tag() / "road_summary.json"))
    t = json.load(open(DER / rid / "m2" / "topo_summary.json"))
    m = json.load(open(DER / rid / "meta.json"))
    rows.append({"road": rid, "length_km": round(s.s_raw.max() / 1000, 2),
                 "deg_per_km": round(r1["deg_per_km"]), "turns_per_km_ge45": round(r1["turns_per_km_45"], 2),
                 "turns_per_km_ge15": round(r1["turns_per_km_15"], 2),
                 "radius_p10_p50_p75_m": f"{r1['radius_p10']:.0f}/{r1['radius_p50']:.0f}/{r1['radius_p75']:.0f}",
                 "pct_length_R_lt_50": round(100 * r1["frac_R_lt_50"], 1), "pct_straight": round(100 * r1["frac_straight"]),
                 "straight_median_m": round(r1["straight_med_m"]), "straight_max_m": round(r1["straight_max_m"]),
                 "gain_m": round(t["gain_m"]), "loss_m": round(t["loss_m"]),
                 "mean_abs_grade_pct": round(t["mean_abs_grade_pct"], 1),
                 "max_sustained_grade_250m_pct": round(t["max_sustained_grade_250m_pct"], 1),
                 "maxspeed_tagged_share": round(m["attr_completeness"]["maxspeed"], 2),
                 "lanes_tagged_share": round(m["attr_completeness"]["lanes"], 2)})
pd.DataFrame(rows).to_csv(FIG / "road_comparison.csv", index=False)
print(pd.DataFrame(rows).set_index("road").T.to_string())
