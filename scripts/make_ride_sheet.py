"""Printable pilot ride sheet: one blank form page + neutral corner-reference pages (no model predictions shown)."""
import json
import pickle
import textwrap
import sys
from pathlib import Path
from urllib.parse import quote

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle

sys.path.insert(0, "src")
from switchback.geometry import Params, build_series, project, segment
from switchback.roadctx import analyse, read_context

D, OUT = Path("data/derived"), Path("reports/ride_pilot")
P = Params()
roads = pickle.load(open(D / "context/roads.pkl", "rb"))
pilot = pickle.load(open(D / "context/pilot_roads.pkl", "rb"))
c211 = pd.read_csv(D / "us211_climb_km6_thornton_gap/centerline_nodes.csv")

# (title, lon, lat, start text, end text, node dict for landmarks)
ROUTES = [
    ("US-211 climb, westbound (up)", c211.lon.values, c211.lat.values, "Sperryville side, 6 km west of the US-522 junction", "Thornton Gap (Skyline Drive entrance)", roads["US-211 climb (reference)"], "us211_w"),
    ("US-211 climb, eastbound (down)", c211.lon.values[::-1], c211.lat.values[::-1], "Thornton Gap (Skyline Drive entrance)", "Sperryville side, 6 km west of the US-522 junction", roads["US-211 climb (reference)"], "us211_e"),
    ("Scenic Drive (Montclair, VA), as numbered", np.array(pilot[6]["lon"]), np.array(pilot[6]["lat"]), "start of the 4 km stretch", "end of the 4 km stretch", pilot[6], "scenic"),
    ("Beach Drive (Kensington, MD), as numbered", np.array(roads["Beach Drive MD (cand. #18)"]["lon"]), np.array(roads["Beach Drive MD (cand. #18)"]["lat"]), "start of the 6 km stretch", "end of the 6 km stretch", roads["Beach Drive MD (cand. #18)"], "beach"),
]


def feel(r):
    return "hairpin" if r < 40 else "tight" if r < 70 else "medium" if r < 120 else "sweeper"


def corner_table(lon, lat):
    ser = build_series(lon, lat, P)
    corners, _ = segment(ser, P)
    c = corners[(~corners.partial) & (corners.angle_deg >= 30)].reset_index(drop=True)
    rows = []
    for i, r in c.iterrows():
        seg = ser[(ser.s >= r.s_start) & (ser.s <= r.s_end)]
        ap = seg.iloc[int(np.argmax(np.abs(seg.kappa.values)))]
        rows.append({"n": i + 1, "side": "L" if r.sign > 0 else "R", "angle": int(round(r.angle_deg)), "radius": int(round(r.min_radius_m)), "feel": feel(r.min_radius_m),
                     "km": round(ap.s / 1000, 2), "lon": ap.lon, "lat": ap.lat, "x": ap.x, "y": ap.y})
    t = pd.DataFrame(rows)
    t["rev"] = len(t) + 1 - t.n
    return ser, t


def gmaps(lon, lat):
    idx = np.linspace(0, len(lon) - 1, 8).round().astype(int)
    wp = quote("|".join(f"{lat[i]:.5f},{lon[i]:.5f}" for i in idx[1:-1]), safe=",")
    return f"https://www.google.com/maps/dir/?api=1&origin={lat[0]:.5f},{lon[0]:.5f}&destination={lat[-1]:.5f},{lon[-1]:.5f}&waypoints={wp}&travelmode=driving"


def page_form():
    fig = plt.figure(figsize=(8.5, 11)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 8.5); ax.set_ylim(0, 11); ax.axis("off")
    T = lambda x, y, s, **k: ax.text(x, y, s, va="top", **k)
    T(.5, 10.7, "Switchback ride sheet", fontsize=16, weight="bold")
    T(.5, 10.35, "Fill in within an hour of the ride (about 5 minutes). Do not fill in while riding.  Rate what you experienced, not what you expected.", fontsize=8)
    box = lambda x, y, w, h, lw=.8: ax.add_patch(Rectangle((x, y), w, h, fill=False, lw=lw))
    # A. ride
    T(.5, 10.0, "A. The ride", fontsize=10, weight="bold")
    lines = [("Road / stretch: ______________________________   Direction: ______________   Date: ____________   Start time: ________", 9.7),
             ("Pace:   ☐ relaxed   ☐ brisk   ☐ spirited          Surface:   ☐ dry   ☐ damp   ☐ wet          Temp (°F):   ☐ <50   ☐ 50-70   ☐ 70-90   ☐ >90", 9.4),
             ("Trees:   ☐ bare   ☐ partly leaved   ☐ full leaf          Traffic vs what I expected:   ☐ lighter   ☐ as expected   ☐ heavier", 9.1),
             ("Oncoming vehicles I passed (best guess): ________      Passed or held up by slower vehicles:   ☐ never   ☐ once or twice   ☐ often", 8.8)]
    for s, y in lines:
        T(.5, y, s, fontsize=8)
    # B. ratings
    T(.5, 8.45, "B. Ratings (circle one; each dimension on its own)", fontsize=10, weight="bold")
    dims = [("Flow / engagement (1 = dull or awkward, 5 = great)", 5), ("Seeing through corners (1 = often blind, 5 = always had enough view)", 5),
            ("Interruptions (1 = flow constantly broken, 5 = never)", 5), ("Pavement (1 = poor, 5 = excellent)", 5), ("Traffic (1 = it spoiled the ride, 5 = no effect)", 5)]
    y = 8.15
    for lab, n in dims:
        T(.5, y, lab, fontsize=8)
        for k in range(1, n + 1):
            ax.add_patch(plt.Circle((6.0 + .38 * (k - 1), y - .07), .12, fill=False, lw=.8)); ax.text(6.0 + .38 * (k - 1), y - .07, str(k), ha="center", va="center", fontsize=7)
        y -= .32
    T(.5, y, "Overall enjoyment (1-10)", fontsize=8, weight="bold")
    for k in range(1, 11):
        ax.add_patch(plt.Circle((2.55 + .34 * (k - 1), y - .07), .12, fill=False, lw=.8)); ax.text(2.55 + .34 * (k - 1), y - .07, str(k), ha="center", va="center", fontsize=7)
    T(.5, y - .3, "Would I ride it again?   \u2610 yes    \u2610 maybe    \u2610 no", fontsize=8, weight="bold")
    # C. marks
    y0 = y - .75
    T(.5, y0, "C. Marks: specific corners or places that stood out (use the corner numbers on the map pages)", fontsize=10, weight="bold")
    cols = [(.5, .45, "#"), (.95, 1.35, "Corner # or place"), (2.3, .8, "Type"), (3.1, .6, "1-5"), (3.7, .75, "One-off?"), (4.45, 3.55, "Note (what you saw or felt)")]
    ytab = y0 - .3
    for x, w, h in cols:
        box(x, ytab - .3, w, .3, 1.2); ax.text(x + .05, ytab - .15, h, fontsize=7, va="center", weight="bold")
    for r in range(1, 10):
        yy = ytab - .3 - .3 * r
        for x, w, h in cols:
            box(x, yy, w, .3, .5)
        ax.text(.52, yy + .15, str(r), fontsize=7, va="center")
    yl = ytab - .3 - .3 * 10 - .12
    T(.5, yl, "Type:  BL blind corner    CL clear corner    GF great flow    AF awkward flow    SU surprise (tightens, off-camber, crest)", fontsize=6.8)
    T(.5, yl - .17, "IN interruption (signal, stop, junction, driveway)    PV pavement    HZ hazard (gravel, debris, animal, water)    TR traffic event", fontsize=6.8)
    T(.5, yl - .34, "1-5 = how strongly.   One-off today = Y if it would not be there on another day (wet, gravel, a slow truck).", fontsize=6.8)
    # D. free text
    yd = yl - .65
    T(.5, yd, "D. Anything about the road that surprised you, or that these questions missed?", fontsize=10, weight="bold")
    box(.5, yd - .95, 7.5, .8, 1.0)
    T(.5, .3, "Hand back: a photo of this page, or the same fields typed into data_private/ride_log.csv and ride_marks.csv. Your ratings stay private.", fontsize=7, style="italic")
    return fig


def page_route(title, lon, lat, start, end, tab, ser, node, key, ctx):
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([.06, .43, .88, .50]); ax2 = fig.add_axes([.06, .04, .88, .35]); ax2.axis("off")
    x, y, _ = project(lon, lat)
    ax.plot((x - x.min()) / 1000, (y - y.min()) / 1000, color="#444444", lw=1.8)
    for _, r in tab.iterrows():
        ax.scatter((r.x - x.min()) / 1000, (r.y - y.min()) / 1000, s=150, color="#8ecae6" if r.side == "L" else "#f4a261", edgecolor="k", lw=.6, zorder=3)
        ax.text((r.x - x.min()) / 1000, (r.y - y.min()) / 1000, str(r.n), ha="center", va="center", fontsize=6.5, zorder=4)
    ax.text((x[0] - x.min()) / 1000, (y[0] - y.min()) / 1000, "START", color="green", weight="bold", fontsize=9, ha="right")
    ax.text((x[-1] - x.min()) / 1000, (y[-1] - y.min()) / 1000, "END", color="red", weight="bold", fontsize=9, ha="left")
    ax.set_aspect("equal"); ax.set_xlabel("km"); ax.set_ylabel("km")
    ax.set_title(f"{title}   (blue = left-hand corner, orange = right-hand, numbers in this direction of travel)", fontsize=9, loc="left")
    T = lambda yy, s, **k: ax2.text(0, yy, s, va="top", transform=ax2.transAxes, **k)
    T(1.0, textwrap.fill(f"Start: {start}.  End: {end}.  Length about {ser.s.max()/1000:.1f} km, {len(tab)} corners of 30 degrees or more.", 110), fontsize=8)
    T(.90, "Route link (Google Maps, approximate):\n" + textwrap.fill(gmaps(lon, lat), 150, break_long_words=True), fontsize=5.5)
    if key in ("scenic", "beach"):
        T(.80, f"Ridden the other way: corner k becomes {len(tab)} + 1 - k, and left/right swap.", fontsize=8)
    rows = [f"{r.n:>2}  {r.side}  {r.angle:>3}°  {r.feel:<8} {r.km:>4.1f} km" + (f"   (other way #{r.rev})" if key in ("scenic", "beach") else (f"   (same as {'eastbound' if key=='us211_w' else 'westbound'} #{r.rev})")) for _, r in tab.iterrows()]
    half = (len(rows) + 1) // 2
    ax2.text(0, .74, "  #  side angle feel     at\n" + "\n".join(rows[:half]), va="top", transform=ax2.transAxes, fontsize=7.2, family="monospace")
    ax2.text(.5, .74, "  #  side angle feel     at\n" + "\n".join(rows[half:]), va="top", transform=ax2.transAxes, fontsize=7.2, family="monospace")
    side = [(p, h, n) for p, h, n in ctx["side_ways"] if n and h not in ("footway", "cycleway", "path", "steps", "track")]
    lm = "; ".join(sorted({f"{n} at {p/1000:.1f} km" for p, h, n in side}, key=lambda s: float(s.split(" at ")[1].split()[0])))
    if key.startswith("us211"):
        lm = "(OSM names no side roads along this stretch)"
    T(.24, textwrap.fill("Side roads along the way (from OpenStreetMap, distance from the start of the map direction):  " + (lm or "none named"), 150), fontsize=6.8)
    T(.05, "Corner numbers are for reference only; the sheet does not show anything the analysis predicts, so your marks stay independent.", fontsize=6.8, style="italic")
    return fig


def main():
    ctxs = {}
    for st, pbf in (("VA", "data/raw/virginia-latest.osm.pbf"), ("MD", "data/raw/maryland-latest.osm.pbf")):
        names = [r for r in ROUTES if r[5]["state"] == st]
        tags, ways = read_context(pbf, set(i for r in names for i in r[5]["node_ids"]))
        for r in names:
            ctxs[r[6]] = analyse(r[5], tags, ways)
    tables = {}
    with PdfPages(OUT / "ride_sheet_complete.pdf") as pdf, PdfPages(OUT / "ride_form_one_page.pdf") as pdf1:
        f = page_form(); pdf.savefig(f); pdf1.savefig(f); plt.close(f)
        for title, lon, lat, st, en, node, key in ROUTES:
            ser, tab = corner_table(lon, lat); tables[key] = tab
            f = page_route(title, lon, lat, st, en, tab, ser, node, key, ctxs[key]); pdf.savefig(f); plt.close(f)
            tab.drop(columns=["x", "y"]).to_csv(OUT / f"corners_{key}.csv", index=False)
            print(key, len(tab), "corners, side roads:", len(ctxs[key]["side_ways"]))
    pickle.dump({k: v for k, v in ctxs.items()}, open(D / "context/pilot_ctx.pkl", "wb"))


if __name__ == "__main__":
    main()
