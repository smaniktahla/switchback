"""Table and figure for the context comparison (traffic, speed environment, interruptions, corner sequences)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

R = Path("reports/context")
d = pd.read_csv(R / "comparison.csv")
d["label"] = d.road.str.replace(r" \(cand\. #(\d+)\)", r" #\1", regex=True).str.replace(" (reference)", "", regex=False)
d["veh_per_hour_avg"] = d.aadt_median / 24
d["peak_hour_veh"] = d.aadt_median * d.k_median
d["oncoming_per_ride"] = (d.aadt_median * 0.5 / 24) * (d.length_km / (35 * 1.609344))
d["weekend_vs_weekday"] = ((7 * d.aadt_median - 5 * d.aawdt_median) / 2) / d.aawdt_median - 1
d.to_csv(R / "comparison_derived.csv", index=False)
plt.rcParams.update({"font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(2, 3, figsize=(15, 8)); y = np.arange(len(d))[::-1]
cols = ["#1f77b4"] + ["#999999"] * (len(d) - 1)
a = ax[0, 0]
a.barh(y, d.per_km_signal + d.per_km_stop + d.per_km_give_way, color="#d62728", label="signals + stop/yield signs")
a.barh(y, d.per_km_pub_junction, left=d.per_km_signal + d.per_km_stop + d.per_km_give_way, color="#ff7f0e", label="public side-road junctions")
a.barh(y, d.per_km_driveway, left=d.per_km_signal + d.per_km_stop + d.per_km_give_way + d.per_km_pub_junction, color="#bbbbbb", label="driveway/service junctions (OSM may be incomplete)")
a.set_yticks(y); a.set_yticklabels(d.label); a.set_title("Interruptions per km", loc="left"); a.legend(fontsize=6.5, loc="upper center", bbox_to_anchor=(.5, -.08))
a = ax[0, 1]; w = .38
a.barh(y + w / 2, d.run_hard_longest_incl_ends_m, w, color="#d62728", label="longest run free of signals / stops (m)")
a.barh(y - w / 2, d.run_hard_or_public_junction_longest_incl_ends_m, w, color="#ff7f0e", label="longest run also free of public junctions (m)")
a.set_yticks(y); a.set_yticklabels([]); a.set_title("Longest uninterrupted run (m, lower bound)", loc="left"); a.legend(fontsize=6.5, loc="upper center", bbox_to_anchor=(.5, -.08))
a = ax[0, 2]
a.barh(y + w / 2, d.longest_corner_chain, w, color="#2ca02c", label="longest chain of corners >= 30 deg, gaps <= 100 m")
a.barh(y - w / 2, d.corners_30deg_per_km, w, color="#98df8a", label="corners >= 30 deg per km")
a.set_yticks(y); a.set_yticklabels([]); a.set_title("Sustained corner sequences", loc="left"); a.legend(fontsize=6.5, loc="upper center", bbox_to_anchor=(.5, -.08))
a = ax[1, 0]
bands = [("lat_share_lt0.1g", "< 0.1 g", "#c7e9c0"), ("lat_share_0.1_0.3g", "0.1-0.3 g", "#74c476"), ("lat_share_0.3_0.5g", "0.3-0.5 g", "#fd8d3c"), ("lat_share_gt0.5g", "> 0.5 g", "#d62728")]
left = np.zeros(len(d))
for k, nm, c in bands:
    v = d[k].fillna(0).values * 100; a.barh(y, v, left=left, color=c, label=nm); left += v
for yi, (ok, mph) in zip(y, zip(d.speed_known, d.speed_median_mph)):
    a.text(101, yi, f"{mph:.0f} mph" if ok > .5 else "limit not tagged", va="center", fontsize=7)
a.set_xlim(0, 100); a.set_yticks(y); a.set_yticklabels(d.label); a.set_xlabel("% of curved length"); a.set_title("Lateral acceleration if ridden at the tagged limit", loc="left"); a.legend(fontsize=6.5, ncol=4, loc="lower center", bbox_to_anchor=(.5, -.32))
a = ax[1, 1]
v = d.aadt_median.fillna(0); a.barh(y, v, color=["#1f77b4" if i == 0 else "#999999" for i in range(len(d))])
for yi, (aad, src, yr, q) in zip(y, zip(d.aadt_median, d.traffic_source.fillna(""), d.year, d.quality.fillna(""))):
    a.text(max(aad, 0) + 150 if aad == aad else 150, yi, f"{aad:,.0f} ({src} {int(yr) if yr == yr else 'yr unknown'}, q={q})" if aad == aad else "no count segment found", va="center", fontsize=7)
a.set_xlim(0, 24000); a.set_yticks(y); a.set_yticklabels([]); a.set_title("Annual average daily traffic, both directions", loc="left")
a = ax[1, 2]
a.barh(y, d.oncoming_per_ride, color=["#1f77b4" if i == 0 else "#999999" for i in range(len(d))])
for yi, (o, p) in zip(y, zip(d.oncoming_per_ride, d.peak_hour_veh)):
    a.text((o if o == o else 0) + .5, yi, (f"{o:.0f} per ride" + (f"; peak-hour flow {p:.0f} veh/h" if p == p else "; no K factor")) if o == o else "-", va="center", fontsize=7)
a.set_xlim(0, 120); a.set_yticks(y); a.set_yticklabels([]); a.set_title("Oncoming vehicles per ride (35 mph, avg hour)", loc="left")
fig.suptitle("US-211 climb (blue) next to look-alikes: each dimension separate, no combined score", fontsize=11)
fig.tight_layout(rect=(0, 0, 1, .96)); fig.savefig(R / "fig1_context_comparison.png", dpi=130)
show = d[["label", "length_km", "speed_median_mph", "count_signal", "count_stop", "count_pub_junction", "count_driveway", "count_crossing", "run_hard_longest_incl_ends_m",
          "run_hard_or_public_junction_longest_incl_ends_m", "longest_corner_chain", "corners_30deg_per_km", "lat_share_gt0.5g", "aadt_median", "trucks_pct", "k_median", "oncoming_per_ride", "weekend_vs_weekday"]]
pd.set_option("display.width", 300, "display.max_columns", 30)
print(show.round(2).T.to_string())
