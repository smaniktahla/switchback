"""VDOT traffic volume: geometry from the ArcGIS layer, 2025 values from the county spreadsheets (join on Link ID)."""
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from pyproj import Transformer

LAYER = "https://services.arcgis.com/p5v98VHDX9Atv3l7/arcgis/rest/services/VDOT_Bidirectional_Traffic_Volume/FeatureServer/0/query"
COLS = ["link_id", "route_name", "route_label", "alias", "phys_jur", "_1", "maint_jur", "_2", "start", "end", "link_len",
        "aadt", "aadt_q", "pct_4tire", "pct_bus", "pct_su2", "pct_su3", "pct_comb1", "pct_comb2", "class_q",
        "k", "k_q", "dir_factor", "aawdt", "aawdt_q", "data_date", "comment"]


def load_county_xlsx(path):
    raw = pd.read_excel(path, header=None, skiprows=7)
    df = raw.iloc[:, :27].copy(); df.columns = COLS
    df["link_id"] = pd.to_numeric(df.link_id, errors="coerce")
    return df.dropna(subset=["link_id"]).astype({"link_id": "int64"})


def fetch_segments(bbox, cache):
    cache = Path(cache)
    if cache.exists():
        return json.load(open(cache))
    r = requests.get(LAYER, params={"f": "geojson", "where": "1=1", "geometry": ",".join(map(str, bbox)), "geometryType": "esriGeometryEnvelope",
                                    "inSR": 4326, "outSR": 4326, "spatialRel": "esriSpatialRelIntersects", "outFields": "*",
                                    "returnGeometry": "true", "resultRecordCount": 2000}, timeout=120).json()
    json.dump(r, open(cache, "w"))
    return r


def join_road(lon, lat, segs, max_dist=25.0, max_angle=30.0, step=10.0):
    """Assign each 10 m sample of the road to the nearest count segment that runs parallel to it."""
    t = Transformer.from_crs(4326, 32618, always_xy=True)
    x, y = t.transform(np.asarray(lon), np.asarray(lat))
    s = np.r_[0.0, np.cumsum(np.hypot(np.diff(x), np.diff(y)))]
    n = max(int(s[-1] / step), 2)
    ps = np.linspace(0, s[-1], n)
    px, py = np.interp(ps, s, x), np.interp(ps, s, y)
    hx, hy = np.gradient(px), np.gradient(py)
    ang = np.degrees(np.arctan2(hy, hx))
    cand = []
    for f in segs["features"]:
        g = f["geometry"]
        parts = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
        for part in parts:
            a = np.array(part)[:, :2]
            sx, sy = t.transform(a[:, 0], a[:, 1])
            cand.append((f["properties"], np.c_[sx, sy]))
    best = [(None, 1e9)] * len(px)
    for k, (prop, pl) in enumerate(cand):
        # densify polyline to ~5 m
        d = np.r_[0.0, np.cumsum(np.hypot(np.diff(pl[:, 0]), np.diff(pl[:, 1])))]
        if d[-1] < 1:
            continue
        m = max(int(d[-1] / 5), 2); dd = np.linspace(0, d[-1], m)
        qx, qy = np.interp(dd, d, pl[:, 0]), np.interp(dd, d, pl[:, 1])
        qa = np.degrees(np.arctan2(np.gradient(qy), np.gradient(qx)))
        for i in range(len(px)):
            dist = np.hypot(qx - px[i], qy - py[i]); j = int(dist.argmin())
            if dist[j] > max_dist or dist[j] >= best[i][1]:
                continue
            da = abs((qa[j] - ang[i] + 90) % 180 - 90)
            if da <= max_angle:
                best[i] = (k, float(dist[j]))
    return ps, [None if b[0] is None else cand[b[0]][0] for b in best]
