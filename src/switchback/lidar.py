"""USGS 3DEP lidar (Entwine Point Tile on the public S3 bucket) -> non-ground occupancy voxels.

EPT thins points on a 3D octree grid, so the union of nodes down to a given depth keeps vertical
structure (trunks, understory, canopy) at roughly the octree cell size. Used to add vegetation and
other above-ground obstructions to the terrain-only sight-distance model.
"""
import io
import json
from pathlib import Path

import laspy
import numpy as np
import requests
from pyproj import Transformer

BASE = "https://usgs-lidar-public.s3.us-west-2.amazonaws.com"
EXCLUDE_CLASSES = {2, 7, 9, 13, 14, 15, 16, 18}    # ground, noise, water, wires/towers
GPS_EPOCH_OFFSET = 1_000_000_000                    # 'adjusted standard GPS time'


def _get(url, cache):
    if cache and cache.exists():
        return cache.read_bytes()
    for k in range(4):
        r = requests.get(url, timeout=120)
        if r.status_code == 200:
            if cache:
                cache.parent.mkdir(parents=True, exist_ok=True); cache.write_bytes(r.content)
            return r.content
        if r.status_code == 404:
            return None
    r.raise_for_status()


def _node_bounds(root, key):
    d, x, y, z = map(int, key.split("-"))
    size = [(root[i + 3] - root[i]) / 2 ** d for i in range(3)]
    return (root[0] + x * size[0], root[1] + y * size[1], root[0] + (x + 1) * size[0], root[1] + (y + 1) * size[1])


def list_nodes(project, bbox_3857, dmax, cache_dir):
    """Node keys (depth <= dmax) whose XY footprint intersects bbox (xmin, ymin, xmax, ymax in EPSG:3857)."""
    ept = json.loads(_get(f"{BASE}/{project}/ept.json", cache_dir / "ept.json"))
    root = ept["bounds"]
    def hit(k):
        b = _node_bounds(root, k)
        return not (b[2] < bbox_3857[0] or b[0] > bbox_3857[2] or b[3] < bbox_3857[1] or b[1] > bbox_3857[3])
    nodes, todo, seen = {}, ["0-0-0-0"], set()
    while todo:
        key = todo.pop()
        if key in seen:
            continue
        seen.add(key)
        h = json.loads(_get(f"{BASE}/{project}/ept-hierarchy/{key}.json", cache_dir / "hier" / f"{key}.json"))
        for k, n in h.items():
            if int(k.split("-")[0]) > dmax or not hit(k):
                continue
            if n == -1:
                todo.append(k)
            elif n > 0:
                nodes[k] = n
    return sorted(nodes), ept


def read_points(project, keys, bbox_3857, cache_dir):
    """Concatenated x, y, z (EPSG:3857 / metres), class, return number, gps time inside bbox."""
    out = []
    for k in keys:
        raw = _get(f"{BASE}/{project}/ept-data/{k}.laz", cache_dir / "data" / f"{k}.laz")
        if raw is None:
            continue
        las = laspy.read(io.BytesIO(raw))
        x, y = np.asarray(las.x), np.asarray(las.y)
        m = (x >= bbox_3857[0]) & (x <= bbox_3857[2]) & (y >= bbox_3857[1]) & (y <= bbox_3857[3])
        if m.any():
            out.append(np.c_[x[m], y[m], np.asarray(las.z)[m], np.asarray(las.classification)[m],
                             np.asarray(las.return_number)[m], np.asarray(las.gps_time)[m]])
    return np.vstack(out) if out else np.empty((0, 6))


def to_utm(pts, epsg):
    t = Transformer.from_crs(3857, epsg, always_xy=True)
    x, y = t.transform(pts[:, 0], pts[:, 1])
    return np.c_[x, y, pts[:, 2:]]


class Voxels:
    """Sorted int64 keys of occupied (vx x vx x vz) cells; vectorised point-in-occupied-cell tests."""

    def __init__(self, xyz, origin, vx=1.5, vz=1.0):
        self.o, self.vx, self.vz = np.asarray(origin, float), vx, vz
        self.keys = np.unique(self._key(xyz[:, 0], xyz[:, 1], xyz[:, 2]))

    def _key(self, x, y, z):
        ix = np.floor((x - self.o[0]) / self.vx).astype(np.int64) + (1 << 20)
        iy = np.floor((y - self.o[1]) / self.vx).astype(np.int64) + (1 << 20)
        iz = np.floor((z - self.o[2]) / self.vz).astype(np.int64) + (1 << 20)
        return (iz << 42) | (iy << 21) | ix

    def occupied(self, x, y, z):
        k = self._key(x, y, z)
        i = np.searchsorted(self.keys, k)
        i[i == len(self.keys)] = 0
        return self.keys[i] == k


def collection_dates(gps):
    """Rough acquisition window (UTC dates) from adjusted GPS time."""
    import datetime as dt
    base = dt.datetime(1980, 1, 6) + dt.timedelta(seconds=0)
    f = lambda s: (base + dt.timedelta(seconds=float(s) + GPS_EPOCH_OFFSET)).date().isoformat()
    return f(np.percentile(gps, 1)), f(np.percentile(gps, 50)), f(np.percentile(gps, 99))
