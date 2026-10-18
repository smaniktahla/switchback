"""Scan a region for 3-10 km stretches that resemble the US-211 climb (the owner's reference ride).

Paved public roads only (see switchback.scan.read_region). A stretch is a run of 1 km windows
(stride 500 m) whose heading change, median radius, turn density and straight share all fall
inside the US-211 climb's own range (+/-25%). Ranked by closeness to the climb's centre.
"""
import json
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from switchback.geometry import Params, analyze, features
from switchback.scan import chain_ways, read_region

DC, RADIUS_KM = (38.9072, -77.0369), 177.0      # ~110 miles straight line as the '2 hours' proxy
STATES = {"virginia": "VA", "maryland": "MD", "west-virginia": "WV"}
OUT, REP = Path("data/derived/scan_dc"), Path("reports/scan_dc")
P = Params()
FEATS = ["deg_per_km", "radius_p50", "turns_per_km_45", "frac_straight"]
MIN_M, MAX_M, WIN_PER_10K = 3000.0, 10000.0, 19
TOL, GAP = 0.40, 2   # matching tolerance around the climb windows; weak windows tolerated inside a run
TEMPLATE_ROAD = "us211_climb_km6_thornton_gap"


def template():
    d = pd.read_csv(f"data/derived/{TEMPLATE_ROAD}/centerline_nodes.csv")
    _, _, _, w, _ = analyze(d.lon.values, d.lat.values, P, window_sizes=(1000,), stride=500)
    w = w[1000]; w = w[~w.partial]
    w = w[w.deg_per_km >= 0.7 * w.deg_per_km.median()]          # drop the straighter lead-in window
    strict = {f: (float(w[f].min() * .75), float(w[f].max() * 1.25)) for f in FEATS}      # the climb's own range +/-25%
    loose = {f: (float(w[f].min() * (1 - TOL)), float(w[f].max() * (1 + TOL))) for f in FEATS}  # used for matching
    return {"loose": loose, "strict": strict}, w


def _score(row, rng):
    s = []
    for f in FEATS:
        lo, hi = rng["strict"][f]; x = row[f]
        s.append(3.0 if x != x else abs(x - (lo + hi) / 2) / ((hi - lo) / 2))
    return float(np.mean(s))


def scan_chain(args):
    ci, key, highway, state, pts, rng = args
    lon = np.array([p[1] for p in pts]); lat = np.array([p[2] for p in pts])
    try:
        ser, corners, straights, wins, road = analyze(lon, lat, P, window_sizes=(1000,), stride=500)
    except Exception:
        return []
    w = wins[1000]; w = w[~w.partial].reset_index(drop=True)
    if len(w) < 5:
        return []
    m = np.ones(len(w), bool)
    for f in FEATS:
        m &= ((w[f] >= rng["loose"][f][0]) & (w[f] <= rng["loose"][f][1])).values
    if not m.any():
        return []
    m2 = m.copy()
    for g in range(1, GAP + 1):                                    # tolerate up to GAP weak windows inside a run
        for i in range(1, n_ := len(m) - g):
            if m[i - 1] and m[i + g] and not m[i:i + g].any():
                m2[i:i + g] = True
    sc = np.array([_score(r, rng) for _, r in w.iterrows()])
    out, i, n = [], 0, len(w)
    while i < n:
        if not m2[i]:
            i += 1; continue
        j = i
        while j + 1 < n and m2[j + 1]:
            j += 1
        a, b = i, j
        if w.s1[b] - w.s0[a] > MAX_M:                            # keep the best 10 km of a long run
            k = WIN_PER_10K
            best = min(range(a, b - k + 2), key=lambda q: sc[q:q + k].mean())
            a, b = best, best + k - 1
        s0, s1 = float(w.s0[a]), float(w.s1[b])
        if s1 - s0 >= MIN_M:
            f = features(ser, corners, straights, s0, s1, P)
            sel = (ser.s >= s0) & (ser.s <= s1)
            out.append({"chain_idx": ci, "road_key": key, "highway": highway, "state": state,
                        "s0": s0, "s1": s1, "length_m": s1 - s0, "score": float(sc[a:b + 1].mean()),
                        "match_share": float(m[a:b + 1].mean()),
                        **{k: f.get(k) for k in ["deg_per_km", "radius_p50", "turns_per_km_45", "turns_per_km_15",
                                                  "frac_straight", "frac_R_lt_50", "straight_max_m"]},
                        "lon": np.round(ser.lon[sel].values, 6).tolist(), "lat": np.round(ser.lat[sel].values, 6).tolist()})
        i = j + 1
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True); REP.mkdir(parents=True, exist_ok=True)
    cache = OUT / "region_ways.pkl"
    if cache.exists():
        ways, places = pickle.load(open(cache, "rb"))
    else:
        ways, places, seen = [], [], set()
        for pbf, st in STATES.items():
            w, pl = read_region(f"data/raw/{pbf}-latest.osm.pbf", st, DC, RADIUS_KM)
            ways += [x for x in w if x["id"] not in seen]; seen.update(x["id"] for x in w); places += pl
            print(f"{st}: {len(w)} ways, {len(pl)} places", flush=True)
        pickle.dump((ways, places), open(cache, "wb"))
    chains = chain_ways(ways)
    long_ = [c for c in chains if sum(a[0] for a in c["attrs"]) >= MIN_M]
    print(f"{len(ways)} ways -> {len(chains)} chains, {len(long_)} chains >= 3 km "
          f"({sum(sum(a[0] for a in c['attrs']) for c in long_) / 1000:.0f} km)", flush=True)
    rng, tw = template()
    print("template (US-211 climb windows, loose):", {k: (round(a, 2), round(b, 2)) for k, (a, b) in rng["loose"].items()}, flush=True)
    state_of = {w["id"]: w["state"] for w in ways}
    jobs = [(i, c["key"], c["highway"], state_of[c["way_ids"][0]], c["pts"], rng) for i, c in enumerate(long_)]
    res = []
    with ProcessPoolExecutor(max_workers=6) as ex:
        for k, r in enumerate(ex.map(scan_chain, jobs, chunksize=20)):
            res += r
            if k % 2000 == 0:
                print(f"  {k}/{len(jobs)} chains, {len(res)} stretches", flush=True)
    print(f"{len(res)} raw stretches", flush=True)
    pickle.dump((res, places, rng), open(OUT / "stretches_loose.pkl", "wb"))


if __name__ == "__main__":
    main()
