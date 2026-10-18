"""Diagnostic plot for M1 (not the final report): signed curvature and corners vs distance."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from switchback.geometry import Params
from switchback.reference import load_roads

tag = Params().tag()
roads = list(load_roads())
fig, ax = plt.subplots(len(roads), 2, figsize=(14, 3.2 * len(roads)), gridspec_kw={"width_ratios": [3, 1]})
for i, rid in enumerate(roads):
    d = Path("data/derived") / rid / "m1" / tag
    s = pd.read_csv(d / "series.csv"); c = pd.read_csv(d / "corners.csv")
    s = s[s.valid]
    a = ax[i, 0]
    a.plot(s.s / 1000, 1000 * s.kappa, lw=0.6)
    a.set_ylabel("signed curvature (1/km)\nleft +"); a.set_title(rid, fontsize=9); a.axhline(0, c="k", lw=0.3)
    a.set_ylim(-80, 80)
    ax[i, 1].plot(s.x - s.x.mean(), s.y - s.y.mean(), lw=0.8); ax[i, 1].set_aspect("equal")
    ax[i, 1].set_xticks([]); ax[i, 1].set_yticks([])
ax[-1, 0].set_xlabel("distance along road (km)")
fig.tight_layout(); fig.savefig("reports/out/m1_diag.png", dpi=110)
