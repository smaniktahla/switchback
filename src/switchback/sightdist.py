"""Available sight distance (ASD) for a motorcycle rider along a directed road centerline.

Per rider position along the lane, how far ahead can the rider see (a) the pavement of their own lane,
(b) a vehicle-height target in the centre of the opposing lane, with the line of sight clipped by terrain
(bare-earth DEM) and optionally by lidar-derived above-ground voxels (vegetation, walls, vehicles).
Visibility only: not a safety guarantee and not a recommended speed. Independent of curvature metrics.
"""
from dataclasses import dataclass

import numpy as np
from scipy.ndimage import gaussian_filter1d

from .geometry import project, resample


@dataclass(frozen=True)
class SightCfg:
    eye_h: float = 1.30          # rider eye height above the road surface, m
    lane_w: float = 3.4          # lane width, m; centreline is the lane edge between the two directions
    rider_off: float = 1.70      # rider's lateral distance right of the centreline, m
    opp_off: float = -1.70       # opposing-lane target position (left of the centreline), m
    path_obj_h: float = 0.15     # pavement hazard height (gravel/debris), m
    opp_obj_h: float = 1.00      # vehicle target height, m
    ds: float = 5.0              # rider/target spacing along the road, m
    max_d: float = 250.0         # cap on reported sight distance, m
    los_step: float = 1.0        # line-of-sight sampling step, m
    terrain_tol: float = 0.15    # DEM noise allowance before terrain counts as blocking, m
    smooth_xy_m: float = 5.0     # centreline smoothing (light, to keep lane geometry faithful), m
    smooth_z_m: float = 10.0     # road-surface elevation smoothing, m
    near_field_m: float = 3.0    # ignore lidar objects within this distance of the eye (rider's own surroundings)


def lane_frame(lon, lat, cfg):
    x, y, epsg = project(np.asarray(lon, float), np.asarray(lat, float))
    xr, yr, _ = resample(x, y, cfg.ds)
    sg = cfg.smooth_xy_m / cfg.ds
    xs, ys = gaussian_filter1d(xr, sg, mode="nearest"), gaussian_filter1d(yr, sg, mode="nearest")
    dx, dy = np.gradient(xs), np.gradient(ys)
    n = np.hypot(dx, dy)
    nx, ny = dy / n, -dx / n                       # unit normal pointing to the right of travel
    s = np.r_[0.0, np.cumsum(np.hypot(np.diff(xs), np.diff(ys)))]
    return {"x": xs, "y": ys, "nx": nx, "ny": ny, "s": s, "epsg": epsg}


def _lane_xy(f, off):
    return np.c_[f["x"] + off * f["nx"], f["y"] + off * f["ny"]]


def road_z(f, off, ground, cfg):
    xy = _lane_xy(f, off)
    return gaussian_filter1d(ground(xy[:, 0], xy[:, 1]), cfg.smooth_z_m / cfg.ds, mode="nearest")


def _asd(path_xy, path_z, path_s, tgt_xy, tgt_z, tgt_h, ground, vox_list, cfg):
    """First-blocked distance for terrain-only and for terrain + each voxel set in vox_list."""
    n, kmax = len(path_xy), int(cfg.max_d / cfg.ds)
    out_t = np.full(n, cfg.max_d); out_v = [np.full(n, cfg.max_d) for _ in vox_list]
    for i in range(n - 1):
        j = np.arange(i + 1, min(n, i + 1 + kmax))
        x0, y0, z0 = path_xy[i, 0], path_xy[i, 1], path_z[i] + cfg.eye_h
        tx, ty, tz = tgt_xy[j, 0], tgt_xy[j, 1], tgt_z[j] + tgt_h
        d = np.hypot(tx - x0, ty - y0)
        L = int(d.max() / cfg.los_step)
        if L < 2:
            continue
        u = (np.arange(1, L + 1) * cfg.los_step)[None, :] / d[:, None]
        valid = u < (1 - 2.0 / d[:, None])                          # stop short of the target itself
        rows = np.nonzero(valid)[0]
        xs = x0 + (tx - x0)[:, None] * u; ys = y0 + (ty - y0)[:, None] * u; zs = z0 + (tz - z0)[:, None] * u
        xv, yv, zv = xs[valid], ys[valid], zs[valid]
        rflat = np.broadcast_to((np.arange(1, L + 1) * cfg.los_step)[None, :], u.shape)[valid]
        blocked_t = np.zeros(len(j), bool)
        blocked_t[rows[ground(xv, yv) > zv + cfg.terrain_tol]] = True
        def first(b):
            k = np.argmax(b) if b.any() else None
            return cfg.max_d if k is None else max(path_s[j[k] - 1] - path_s[i], 0.0)
        out_t[i] = first(blocked_t)
        for q, vox in enumerate(vox_list):
            bv = blocked_t.copy()
            bv[rows[vox.occupied(xv, yv, zv) & (rflat > cfg.near_field_m)]] = True
            out_v[q][i] = first(bv)
    out_t[-1] = out_v and cfg.max_d or cfg.max_d
    return out_t, out_v


def asd_components(lon, lat, ground, vox_list=(), cfg=SightCfg()):
    """ASD profiles (terrain-only and with each voxel set) for the pavement of the rider's lane and
    for a vehicle in the opposing lane's centre, at every cfg.ds metres along the road."""
    f = lane_frame(lon, lat, cfg)
    z_path = road_z(f, cfg.rider_off, ground, cfg)
    z_opp = road_z(f, cfg.opp_off, ground, cfg)
    pxy, oxy = _lane_xy(f, cfg.rider_off), _lane_xy(f, cfg.opp_off)
    path_t, path_v = _asd(pxy, z_path, f["s"], pxy, z_path, cfg.path_obj_h, ground, list(vox_list), cfg)
    opp_t, opp_v = _asd(pxy, z_path, f["s"], oxy, z_opp, cfg.opp_obj_h, ground, list(vox_list), cfg)
    return f, {"path_terrain": path_t, "opp_terrain": opp_t,
               **{f"path_veg{q}": v for q, v in enumerate(path_v)}, **{f"opp_veg{q}": v for q, v in enumerate(opp_v)}}, z_path


def ssd_m(mph, grade=0.0, t_react=2.5, decel=3.4):
    """AASHTO-style stopping sight distance: reaction + braking, grade-adjusted (grade > 0 uphill)."""
    v = mph * 0.44704
    a = max(decel + 9.81 * grade, 0.5)
    return v * t_react + v * v / (2 * a)
