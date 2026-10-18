"""Intersection-independent geometry measurements on a directed centerline.

Pipeline: project to UTM -> resample at fixed arc-length step -> smooth ->
heading / signed curvature -> corner & straightaway segmentation -> window features.
Nothing here depends on GraphHopper. Sign convention: kappa > 0 is a left turn.
"""
from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.ndimage import gaussian_filter1d
from scipy.signal import savgol_filter


@dataclass(frozen=True)
class Params:
    ds: float = 10.0               # resample step, m
    smooth: str = "gaussian"       # gaussian | savgol | none
    sigma_m: float = 15.0          # gaussian sigma, or savgol window length, m
    r_straight: float = 500.0      # radius above which a sample counts as straight, m
    gap_merge_m: float = 30.0      # same-sign corners separated by a shorter straight are merged
    angle_thrs: tuple = (15, 30, 45, 60, 90)   # 'significant turn' thresholds, degrees
    rhythm_angle: float = 30.0     # corners >= this angle feed the (experimental) rhythm features
    chain_gap_m: float = 50.0      # corners closer than this belong to one chain

    def tag(self):
        return f"ds{self.ds:g}_{self.smooth}{self.sigma_m:g}_R{self.r_straight:g}"


def utm_epsg(lon, lat):
    return (32600 if lat >= 0 else 32700) + int((lon + 180) // 6) + 1


def project(lon, lat):
    epsg = utm_epsg(float(np.mean(lon)), float(np.mean(lat)))
    x, y = Transformer.from_crs(4326, epsg, always_xy=True).transform(lon, lat)
    return np.asarray(x), np.asarray(y), epsg


def resample(x, y, ds):
    s = np.r_[0.0, np.cumsum(np.hypot(np.diff(x), np.diff(y)))]
    n = max(int(round(s[-1] / ds)), 2)
    s_new = np.linspace(0.0, s[-1], n + 1)
    return np.interp(s_new, s, x), np.interp(s_new, s, y), s[-1]


def smooth_xy(x, y, p):
    """Returns smoothed x, y and the end trim (m) that is contaminated by edge effects."""
    if p.smooth == "none" or p.sigma_m <= 0:
        return x, y, 2 * p.ds
    if p.smooth == "gaussian":
        sg = p.sigma_m / p.ds
        return (gaussian_filter1d(x, sg, mode="nearest"),
                gaussian_filter1d(y, sg, mode="nearest"), 3 * p.sigma_m)
    if p.smooth == "savgol":
        w = max(int(round(p.sigma_m / p.ds)) | 1, 7)
        return savgol_filter(x, w, 3), savgol_filter(y, w, 3), p.sigma_m / 2 + p.ds
    raise ValueError(p.smooth)


def derive(x, y, trim_m):
    dx, dy = np.gradient(x), np.gradient(y)
    step = np.hypot(dx, dy)
    th = np.unwrap(np.arctan2(dy, dx))
    kappa = np.gradient(th) / step
    s = np.r_[0.0, np.cumsum(np.hypot(np.diff(x), np.diff(y)))]
    valid = (s >= trim_m) & (s <= s[-1] - trim_m)
    return pd.DataFrame({"s": s, "x": x, "y": y, "heading": th, "kappa": kappa,
                         "step": step, "valid": valid})


def build_series(lon, lat, p):
    x, y, epsg = project(np.asarray(lon, float), np.asarray(lat, float))
    xr, yr, raw_len = resample(x, y, p.ds)
    xs, ys, trim = smooth_xy(xr, yr, p)
    ser = derive(xs, ys, trim)
    ser["xr"], ser["yr"] = xr, yr          # unsmoothed resampled centerline (for DEM sampling)
    ser["s_raw"] = np.r_[0.0, np.cumsum(np.hypot(np.diff(xr), np.diff(yr)))]
    inv = Transformer.from_crs(epsg, 4326, always_xy=True)
    ser["lon"], ser["lat"] = inv.transform(ser.x.values, ser.y.values)
    ser.attrs.update(raw_len=raw_len, trim=trim, epsg=epsg)
    return ser


def segment(ser, p):
    """Corner and straightaway segmentation on valid samples."""
    s, k, step = ser.s.values, ser.kappa.values, ser.step.values
    k0 = 1.0 / p.r_straight
    cls = np.where(k > k0, 1, np.where(k < -k0, -1, 0))
    cls = np.where(ser.valid.values, cls, 2)
    cut = np.flatnonzero(np.diff(cls)) + 1
    a_, b_ = np.r_[0, cut], np.r_[cut, len(cls)]
    runs = [(a, b, c) for a, b, c in zip(a_, b_, cls[a_])]
    corners, straights, last_run = [], [], -10
    consumed = set()
    for i, (a, b, c) in enumerate(runs):
        if c not in (1, -1):
            continue
        if (corners and corners[-1]["sign"] == c and i == last_run + 2 and runs[i - 1][2] == 0
                and s[b - 1] - s[runs[i - 1][0]] >= 0 and s[a] - s[runs[i - 1][0]] <= p.gap_merge_m):
            corners[-1]["b"] = b
            consumed.add(i - 1)
        else:
            corners.append({"a": a, "b": b, "sign": int(c)})
        last_run = i
    rows = []
    for c in corners:
        a, b = c["a"], c["b"]
        sl = slice(a, b)
        partial = (a > 0 and cls[a - 1] == 2) or (b < len(cls) and cls[b] == 2)
        rows.append({"s_start": s[a], "s_end": s[b - 1], "length_m": s[b - 1] - s[a] + np.mean(step[sl]),
                     "sign": c["sign"], "angle_deg": abs(np.degrees(np.sum(k[sl] * step[sl]))),
                     "min_radius_m": 1.0 / np.max(np.abs(k[sl])), "partial": bool(partial)})
    corners_df = pd.DataFrame(rows, columns=["s_start", "s_end", "length_m", "sign", "angle_deg",
                                             "min_radius_m", "partial"])
    corners_df["partial"] = corners_df["partial"].astype(bool)
    srows = []
    for i, (a, b, c) in enumerate(runs):
        if c == 0 and i not in consumed:
            partial = (a > 0 and cls[a - 1] == 2) or (b < len(cls) and cls[b] == 2)
            srows.append({"s_start": s[a], "s_end": s[b - 1],
                          "length_m": s[b - 1] - s[a] + np.mean(step[a:b]), "partial": bool(partial)})
    straights_df = pd.DataFrame(srows, columns=["s_start", "s_end", "length_m", "partial"])
    straights_df["partial"] = straights_df["partial"].astype(bool)
    return corners_df, straights_df


def features(ser, corners, straights, s0, s1, p):
    """Feature vector for the span [s0, s1). Corners/straights belong to a span by midpoint."""
    m = (ser.s.values >= s0) & (ser.s.values < s1) & ser.valid.values
    k, st = ser.kappa.values[m], ser.step.values[m]
    L = float(st.sum())
    f = {"length_m": L}
    if L <= 0:
        return f
    ak = np.abs(k)
    f["deg_per_km"] = float(np.degrees(np.sum(ak * st)) / (L / 1000))
    curved = ak > 1.0 / p.r_straight
    f["frac_straight"] = float(1 - st[curved].sum() / L)
    rad = 1.0 / ak[curved]
    for q in (10, 25, 50, 75):
        f[f"radius_p{q}"] = float(np.percentile(rad, q)) if len(rad) else np.nan
    for r in (30, 50, 100, 200):
        f[f"frac_R_lt_{r}"] = float(st[ak > 1.0 / r].sum() / L)
    sx = ser.x.values[m]; sy = ser.y.values[m]
    f["chord_ratio"] = float(np.hypot(sx[-1] - sx[0], sy[-1] - sy[0]) / L)
    c = corners[~corners.partial]
    c = c[((c.s_start + c.s_end) / 2 >= s0) & ((c.s_start + c.s_end) / 2 < s1)]
    for t in p.angle_thrs:
        f[f"turns_per_km_{t}"] = float((c.angle_deg >= t).sum() / (L / 1000))
    sg = straights[~straights.partial]
    sg = sg[((sg.s_start + sg.s_end) / 2 >= s0) & ((sg.s_start + sg.s_end) / 2 < s1)]
    f["straight_n"] = int(len(sg))
    f["straight_med_m"] = float(sg.length_m.median()) if len(sg) else np.nan
    f["straight_mean_m"] = float(sg.length_m.mean()) if len(sg) else np.nan
    f["straight_max_m"] = float(sg.length_m.max()) if len(sg) else np.nan
    r = c[c.angle_deg >= p.rhythm_angle].sort_values("s_start")
    f["rhythm_n"] = int(len(r))
    if len(r) >= 2:
        gap = (r.s_start.values[1:] - r.s_end.values[:-1]).clip(min=0)
        f["rhythm_gap_med_m"] = float(np.median(gap))
        f["rhythm_gap_cv"] = float(np.std(gap) / np.mean(gap)) if np.mean(gap) > 0 else np.nan
        f["rhythm_alternation"] = float(np.mean(r.sign.values[1:] != r.sign.values[:-1]))
        chains, cur = [], 1
        for g in gap:
            if g <= p.chain_gap_m:
                cur += 1
            else:
                chains.append(cur); cur = 1
        chains.append(cur)
        f["chain_med"], f["chain_max"] = float(np.median(chains)), int(max(chains))
    return f


def windows(ser, corners, straights, W, p, stride=None):
    stride = stride or W
    v = ser.s[ser.valid]
    lo, hi = float(v.min()), float(v.max())
    rows, i, s0 = [], 0, lo
    while s0 + 0.5 * W <= hi:
        s1 = min(s0 + W, hi + 1e-6)
        f = features(ser, corners, straights, s0, s1, p)
        mid = ser.iloc[(ser.s - (s0 + s1) / 2).abs().argmin()]
        rows.append({"window_idx": i, "window_m": W, "stride_m": stride, "s0": s0, "s1": s1,
                     "partial": bool(s1 - s0 < W - 1), "lon_mid": mid.lon, "lat_mid": mid.lat, **f})
        i += 1; s0 += stride
    return pd.DataFrame(rows)


def analyze(lon, lat, p, window_sizes=(500, 1000, 2000), stride=None):
    ser = build_series(lon, lat, p)
    corners, straights = segment(ser, p)
    v = ser.s[ser.valid]
    road = features(ser, corners, straights, float(v.min()), float(v.max()) + 1e-6, p)
    road.update(raw_polyline_len_m=ser.attrs["raw_len"], analyzed_m=road["length_m"],
                trimmed_each_end_m=ser.attrs["trim"], n_corners=int((~corners.partial).sum()))
    wins = {W: windows(ser, corners, straights, W, p, stride) for W in window_sizes}
    return ser, corners, straights, wins, road


def calibrate_radius(p, radii=(20, 30, 50, 75, 100, 150, 200, 300, 500), node_spacing=15.0,
                     noise_m=0.0, seed=0):
    """Recover known radii from synthetic arcs sampled like OSM vertices; returns {R: R_est/R}."""
    rng = np.random.default_rng(seed)
    out = {}
    for R in radii:
        arc = min(max(8 * p.sigma_m, 250.0), np.pi * R * 1.5)
        lead = 4 * p.sigma_m + 100
        n_arc = max(int(arc / node_spacing), 8)
        t = np.linspace(0, arc / R, n_arc)
        ax, ay = R * np.sin(t), R * (1 - np.cos(t))
        lx = np.arange(-lead, 0, node_spacing)
        ex, ey = ax[-1] + np.cos(t[-1]) * np.arange(node_spacing, lead, node_spacing), \
                 ay[-1] + np.sin(t[-1]) * np.arange(node_spacing, lead, node_spacing)
        x = np.r_[lx, ax, ex] + rng.normal(0, noise_m, len(lx) + len(ax) + len(ex))
        y = np.r_[np.zeros(len(lx)), ay, ey] + rng.normal(0, noise_m, len(lx) + len(ax) + len(ex))
        xr, yr, _ = resample(x, y, p.ds)
        xs, ys, trim = smooth_xy(xr, yr, p)
        ser = derive(xs, ys, trim)
        s_arc0 = lead
        sel = (ser.s > s_arc0 + 0.25 * arc) & (ser.s < s_arc0 + 0.75 * arc) & ser.valid
        kk = np.abs(ser.kappa[sel])
        out[R] = float(1.0 / np.median(kk) / R) if len(kk) else np.nan
    return out


def min_reliable_radius(cal, tol=0.2):
    ok = [R for R in sorted(cal) if all(abs(cal[r] - 1) <= tol for r in cal if r >= R)]
    return min(ok) if ok else None
