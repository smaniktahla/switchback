"""Chain OSM ways into continuous road centerlines and measure windows along them.

Used for the 'ordinary roads' baseline now, and for scanning a region for roads that resemble
the reference roads later. Pure OSM geometry; no routing engine involved.
"""
from collections import defaultdict

import numpy as np
import osmium
import pandas as pd

from .geometry import Params, analyze

DRIVABLE = {"trunk", "primary", "secondary", "tertiary", "unclassified"}
UNPAVED = {"unpaved", "gravel", "dirt", "ground", "compacted", "fine_gravel", "sand", "grass", "mud", "earth", "dirt/sand"}


def _way_len(pts):
    lon = np.radians([p[1] for p in pts]); lat = np.radians([p[2] for p in pts])
    a = np.sin(np.diff(lat) / 2) ** 2 + np.cos(lat[:-1]) * np.cos(lat[1:]) * np.sin(np.diff(lon) / 2) ** 2
    return float(2 * 6371008.8 * np.arcsin(np.sqrt(a)).sum())


def read_ways(pbf, classes=DRIVABLE, exclude_ids=()):
    exclude = set(exclude_ids)
    ways = []
    for o in osmium.FileProcessor(str(pbf), osmium.osm.NODE | osmium.osm.WAY).with_locations():
        if not o.is_way() or o.id in exclude:
            continue
        hw = o.tags.get("highway")
        if hw not in classes or o.tags.get("area") == "yes":
            continue
        pts = [(n.ref, n.lon, n.lat) for n in o.nodes if n.location.valid()]
        if len(pts) < 2:
            continue
        ways.append({"id": o.id, "highway": hw, "ref": o.tags.get("ref", ""), "name": o.tags.get("name", ""),
                     "surface": o.tags.get("surface", ""), "maxspeed": o.tags.get("maxspeed", ""),
                     "oneway": o.tags.get("oneway") in ("yes", "true", "1"), "pts": pts})
    return ways


def _key(w):
    return w["ref"] or w["name"] or f"unnamed:{w['id']}"


def chain_ways(ways):
    """Join ways that share an end node and the same ref/name (only when exactly two ways meet there)."""
    groups = defaultdict(list)
    for w in ways:
        groups[_key(w)].append(w)
    chains = []
    for key, ws in groups.items():
        ends = defaultdict(list)
        for i, w in enumerate(ws):
            ends[w["pts"][0][0]].append((i, 0)); ends[w["pts"][-1][0]].append((i, 1))
        used, nbr = set(), {}
        for node, lst in ends.items():
            if len(lst) == 2 and lst[0][0] != lst[1][0]:
                nbr[lst[0]] = lst[1]; nbr[lst[1]] = lst[0]

        def walk(start, enter_side):
            """Collect points from way `start`, entered at `enter_side` (0 = its first node)."""
            pts, ids, c, es = [], [], start, enter_side
            while c not in used:
                w = ws[c]
                seg = w["pts"] if es == 0 else w["pts"][::-1]
                pts.extend(seg if not pts else seg[1:]); ids.append(w["id"]); used.add(c)
                nx = nbr.get((c, 1 - es))
                if nx is None:
                    break
                c, es = nx
            return pts, ids

        order = [i for i in range(len(ws)) if (i, 0) not in nbr or (i, 1) not in nbr] + list(range(len(ws)))
        for i in order:
            if i in used:
                continue
            free_side = 0 if (i, 0) not in nbr else (1 if (i, 1) not in nbr else 0)
            pts, ids = walk(i, free_side)
            by_id = {w["id"]: w for w in ws}
            attrs = [(_way_len(by_id[x]["pts"]), by_id[x]["surface"], by_id[x]["maxspeed"]) for x in ids]
            chains.append({"key": key, "way_ids": ids, "highway": ws[i]["highway"], "pts": pts, "attrs": attrs})
    return chains


def measure_chains(chains, p=Params(), window_m=1000, min_len_m=1500):
    rows = []
    for ci, c in enumerate(chains):
        lon = np.array([q[1] for q in c["pts"]]); lat = np.array([q[2] for q in c["pts"]])
        if len(lon) < 3:
            continue
        try:
            ser, corners, straights, wins, road = analyze(lon, lat, p, window_sizes=(window_m,))
        except Exception:
            continue
        if road.get("length_m", 0) < min_len_m:
            continue
        w = wins[window_m]
        w = w[~w.partial].copy()
        w["chain_idx"], w["road_key"], w["highway"] = ci, c["key"], c["highway"]
        w["n_ways"] = len(c["way_ids"])
        L = sum(a[0] for a in c["attrs"]) or 1.0
        w["chain_km"] = L / 1000
        w["chain_unpaved_share"] = sum(a[0] for a in c["attrs"] if a[1] in UNPAVED) / L
        w["chain_surface_tagged"] = sum(a[0] for a in c["attrs"] if a[1]) / L
        w["chain_maxspeed_tagged"] = sum(a[0] for a in c["attrs"] if a[2]) / L
        rows.append(w)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def longest_runs(w, group_col, thr, feature="deg_per_km"):
    """Longest run of consecutive windows with `feature` >= thr, per road/chain (sustained twistiness)."""
    rows = []
    for key, g in w.sort_values([group_col, "window_idx"]).groupby(group_col):
        best, cur, start, best_start = 0, 0, None, None
        for idx, v in zip(g.window_idx, g[feature]):
            if v >= thr:
                if cur == 0:
                    start = idx
                cur += 1
                if cur > best:
                    best, best_start = cur, start
            else:
                cur = 0
        rows.append({group_col: key, "longest_run_windows": best, "run_start_idx": best_start, "windows": len(g),
                     "share_above": float((g[feature] >= thr).mean())})
    return pd.DataFrame(rows)


PAVED = {"asphalt", "paved", "concrete", "concrete:plates", "concrete:lanes", "paving_stones", "chipseal", "bituminous"}
PLACES = {"city", "town", "village", "hamlet"}
SOLID = {"trunk", "primary", "secondary", "tertiary"}   # untagged surface is assumed paved only for these


def _km_from(center, lon, lat):
    return float(np.hypot((lon - center[1]) * 111.32 * np.cos(np.radians(center[0])), (lat - center[0]) * 110.57))


def read_region(pbf, state, center, radius_km):
    """Paved, public, drivable ways within radius_km of center (lat, lon), plus place-name nodes.

    Paved rule: explicit unpaved surfaces are dropped; an untagged surface is accepted only for
    trunk/primary/secondary/tertiary; 'unclassified' needs an explicit paved surface tag.
    """
    ways, places = [], []
    for o in osmium.FileProcessor(str(pbf), osmium.osm.NODE | osmium.osm.WAY).with_locations():
        if o.is_node():
            if o.tags.get("place") in PLACES and o.tags.get("name") and o.location.valid():
                places.append((o.tags["name"], o.location.lon, o.location.lat, o.tags["place"]))
            continue
        t = o.tags
        hw = t.get("highway")
        if hw not in DRIVABLE or t.get("area") == "yes":
            continue
        if t.get("access") in ("private", "no") or t.get("motor_vehicle") in ("no", "private"):
            continue
        s = t.get("surface", "")
        if s in UNPAVED or (hw not in SOLID and s not in PAVED):
            continue
        pts = [(n.ref, n.lon, n.lat) for n in o.nodes if n.location.valid()]
        if len(pts) < 2:
            continue
        mid = pts[len(pts) // 2]
        if _km_from(center, mid[1], mid[2]) > radius_km:
            continue
        ways.append({"id": o.id, "highway": hw, "ref": t.get("ref", ""), "name": t.get("name", ""),
                     "surface": s, "maxspeed": t.get("maxspeed", ""),
                     "oneway": t.get("oneway") in ("yes", "true", "1"), "pts": pts, "state": state})
    return ways, places
