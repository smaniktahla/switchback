"""USGS 3DEP elevation along a centerline: corridor tile fetch, sampling, grade metrics."""
import io
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from PIL import Image
from scipy.ndimage import gaussian_filter1d, map_coordinates

EXPORT = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage"
TILE_M = 1000.0
PAD_PX = 3


def _fetch_tile(xmin, ymin, xmax, ymax, res, epsg, tries=4):
    n_x, n_y = int(round((xmax - xmin) / res)), int(round((ymax - ymin) / res))
    for k in range(tries):
        try:
            r = requests.get(EXPORT, params=dict(
                bbox=f"{xmin},{ymin},{xmax},{ymax}", bboxSR=epsg, imageSR=epsg, size=f"{n_x},{n_y}",
                format="tiff", pixelType="F32", interpolation="RSP_BilinearInterpolation", f="image"),
                timeout=120)
            r.raise_for_status()
            a = np.array(Image.open(io.BytesIO(r.content)), dtype="float32")
            if a.shape != (n_y, n_x):
                raise ValueError(f"tile shape {a.shape} != {(n_y, n_x)}")
            return a
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(2 * (k + 1))


class DemSampler:
    """Corridor tiles of a 3DEP DEM at a given pixel size, cached on disk, bilinear sampling."""

    def __init__(self, cache_dir, res, epsg):
        self.dir, self.res, self.epsg = Path(cache_dir), float(res), epsg
        self.dir.mkdir(parents=True, exist_ok=True)
        self.tiles = {}

    def _tile(self, ix, iy):
        """Tile with padding. The service sporadically 502s for particular image sizes, so on failure
        the pad is widened by a pixel and the tile re-requested; the geometry used is stored with it."""
        key = (ix, iy)
        if key in self.tiles:
            return self.tiles[key]
        f = self.dir / f"t_{ix}_{iy}.npz"
        if f.exists():
            z = np.load(f)
            res = (z["a"], float(z["xmin"]), float(z["ymax"]))
        else:
            err = None
            for pad_px in range(PAD_PX, PAD_PX + 6):
                pad = pad_px * self.res
                xmin, ymin = ix * TILE_M - pad, iy * TILE_M - pad
                xmax, ymax = (ix + 1) * TILE_M + pad, (iy + 1) * TILE_M + pad
                try:
                    a = _fetch_tile(xmin, ymin, xmax, ymax, self.res, self.epsg, tries=2)
                    break
                except requests.HTTPError as e:
                    err = e
            else:
                raise err
            np.savez(f, a=a, xmin=xmin, ymax=ymax)
            res = (a, xmin, ymax)
        self.tiles[key] = res
        return res

    def sample(self, x, y):
        x, y = np.asarray(x, float), np.asarray(y, float)
        out = np.full(len(x), np.nan)
        ix, iy = np.floor(x / TILE_M).astype(int), np.floor(y / TILE_M).astype(int)
        for key in set(zip(ix, iy)):
            m = (ix == key[0]) & (iy == key[1])
            a, xmin, ymax = self._tile(*key)
            col = (x[m] - xmin) / self.res - 0.5
            row = (ymax - y[m]) / self.res - 0.5
            out[m] = map_coordinates(a, [row, col], order=1, mode="nearest")
        return out


def sample_profile(ser, sampler, lateral_m=0.0):
    """Elevation at each resampled (unsmoothed) centerline point. lateral_m > 0 takes the median of
    samples at 0, +-lateral/2, +-lateral across the road to damp centerline-offset artifacts."""
    x, y = ser.xr.values, ser.yr.values
    if lateral_m <= 0:
        return sampler.sample(x, y)
    dx, dy = np.gradient(x), np.gradient(y)
    n = np.hypot(dx, dy)
    nx, ny = -dy / n, dx / n
    offs = [0, lateral_m / 2, -lateral_m / 2, lateral_m, -lateral_m]
    return np.median([sampler.sample(x + o * nx, y + o * ny) for o in offs], axis=0)


def add_topography(ser, ele_raw, sigma_m):
    """Adds ele_raw, ele (distance-smoothed) and grade (signed, m/m) using true path length."""
    ds = float(np.median(np.diff(ser.s_raw)))
    ele = gaussian_filter1d(ele_raw, sigma_m / ds, mode="nearest") if sigma_m > 0 else ele_raw.copy()
    ser = ser.copy()
    ser["ele_raw"], ser["ele"] = ele_raw, ele
    ser["grade"] = np.gradient(ele) / np.gradient(ser.s_raw.values)
    return ser


def topo_features(ser, s0, s1, sustain_m=(100, 250, 500)):
    m = ((ser.s.values >= s0) & (ser.s.values < s1) & ser.valid.values)
    if m.sum() < 3:
        return {}
    ds = np.gradient(ser.s_raw.values)[m]
    L = float(ds.sum())
    ele, raw, g = ser.ele.values[m], ser.ele_raw.values[m], ser.grade.values[m]
    d = np.diff(ele)
    f = {"gain_m": float(d[d > 0].sum()), "loss_m": float(-d[d < 0].sum()), "net_m": float(ele[-1] - ele[0]),
         "ele_min_m": float(ele.min()), "ele_max_m": float(ele.max()),
         "raw_gain_m": float(np.diff(raw).clip(min=0).sum())}
    f["climb_m_per_km"] = (f["gain_m"] + f["loss_m"]) / (L / 1000)
    f["mean_abs_grade_pct"] = float(100 * np.mean(np.abs(g)))
    f["grade_p95_abs_pct"] = float(100 * np.percentile(np.abs(g), 95))
    f["grade_std_pct"] = float(100 * np.std(g))
    step = float(np.median(ds))
    for sm in sustain_m:
        k = max(int(round(sm / step)), 1)
        if len(ele) > k:
            f[f"max_sustained_grade_{sm}m_pct"] = float(100 * np.max(np.abs(ele[k:] - ele[:-k])) / (k * step))
    ak = np.abs(ser.kappa.values[m])
    if len(ak) >= 10 and np.std(ak) > 0 and np.std(np.abs(g)) > 0:
        a, b = pd.Series(ak).rank(), pd.Series(np.abs(g)).rank()
        f["spearman_curv_vs_abs_grade"] = float(np.corrcoef(a, b)[0, 1])
    return f


def deck_interpolate(ele, deck):
    """Bare-earth DEMs drop into the valley under bridges/viaducts. Replace elevations on deck samples
    with a straight line between the approach elevations on either side."""
    ele = np.asarray(ele, float).copy()
    deck = np.asarray(deck, bool)
    i, n = 0, len(ele)
    while i < n:
        if deck[i]:
            j = i
            while j + 1 < n and deck[j + 1]:
                j += 1
            a, b = max(i - 1, 0), min(j + 1, n - 1)
            if b > a:
                ele[i:j + 1] = np.interp(np.arange(i, j + 1), [a, b], [ele[a], ele[b]])
            i = j + 1
        else:
            i += 1
    return ele
