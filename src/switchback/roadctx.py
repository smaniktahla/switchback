"""Road-context measurements from OSM: speed environment, interruptions (signals, stops, junctions, access
points) and uninterrupted run lengths. Pure descriptive measurements, no scoring."""
import math
import re

import numpy as np
import osmium

PUBLIC = {"motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential", "living_street"}
TRAIL = {"track", "path", "footway", "cycleway", "bridleway", "steps", "pedestrian"}
HARD = ("signal", "stop", "give_way", "mini_roundabout", "level_crossing")


def hav(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * 6371008.8 * math.asin(math.sqrt(a))


def read_context(pbf, node_ids):
    """Tags of the road's own nodes, and every highway way touching one of them."""
    ids = set(int(i) for i in node_ids)
    tags, ways = {}, {}
    for n in osmium.FileProcessor(str(pbf), osmium.osm.NODE).with_filter(osmium.filter.IdFilter(ids)):
        if len(n.tags):
            tags[n.id] = dict(n.tags)
    for w in osmium.FileProcessor(str(pbf), osmium.osm.WAY).with_filter(osmium.filter.KeyFilter("highway")):
        refs = [n.ref for n in w.nodes]
        if ids.intersection(refs):
            ways[w.id] = {"tags": dict(w.tags), "nodes": refs}
    return tags, ways


def parse_mph(v):
    if v is None:
        return None
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*(mph|km/h|kph)?\s*$", str(v))
    if not m:
        return None
    x = float(m.group(1))
    return x / 1.609344 if m.group(2) in ("km/h", "kph") else x     # unitless values are mph in the US


def speed_category(t):
    if "maxspeed" not in t:
        return "missing"
    typ, src = t.get("maxspeed:type", ""), t.get("source:maxspeed", "")
    if typ == "sign" or "sign" in src or "survey" in src:
        return "posted"
    if typ.startswith(("US:", "implicit", "default")) or "default" in src or "implicit" in src:
        return "legal default"
    return "tagged (source unspecified)"


def analyse(road, tags, ways):
    ids = [int(i) for i in road["node_ids"]]
    lon, lat = np.array(road["node_lon"]), np.array(road["node_lat"])
    seg = np.array([hav(lon[i], lat[i], lon[i + 1], lat[i + 1]) for i in range(len(ids) - 1)])
    cum = np.r_[0.0, np.cumsum(seg)]
    L = float(cum[-1])
    idx = {n: k for k, n in enumerate(ids)}
    # own ways: share two or more road nodes; edge -> way lookup
    own, edge_way = {}, {}
    for wid, w in ways.items():
        shared = [n for n in w["nodes"] if n in idx]
        if len(shared) >= 2:
            own[wid] = w
            for a, b in zip(w["nodes"], w["nodes"][1:]):
                if a in idx and b in idx and abs(idx[a] - idx[b]) == 1:
                    edge_way.setdefault(min(idx[a], idx[b]), wid)
    # ---- speed environment per edge
    spd, cat = np.full(len(seg), np.nan), ["missing"] * len(seg)
    for e in range(len(seg)):
        wid = edge_way.get(e)
        if wid is None:
            continue
        t = ways[wid]["tags"]; spd[e] = parse_mph(t.get("maxspeed")) if parse_mph(t.get("maxspeed")) is not None else np.nan
        cat[e] = speed_category(t) if not np.isnan(spd[e]) else "missing"
    known = ~np.isnan(spd)
    out = {"length_km": L / 1000, "own_ways": len(own)}
    out["speed_known_share"] = float(seg[known].sum() / L)
    cats = {}
    for c, s in zip(cat, seg):
        cats[c] = cats.get(c, 0.0) + s
    out["speed_category_share"] = {k: round(v / L, 3) for k, v in cats.items()}
    if known.any():
        order = np.argsort(spd[known]); cs = np.cumsum(seg[known][order]); med = spd[known][order][np.searchsorted(cs, cs[-1] / 2)]
        out["speed_median_mph"] = float(med)
        for lo, hi, nm in ((0, 25, "le25"), (25, 35, "30_35"), (35, 45, "40_45"), (45, 99, "50plus")):
            out[f"speed_share_{nm}"] = float(seg[known & (spd > lo) & (spd <= hi)].sum() / seg[known].sum())
        sk = spd[known]
        out["speed_changes_per_km"] = float((np.abs(np.diff(sk)) > 0.5).sum() / (L / 1000))
    # ---- events at nodes
    ev = {k: [] for k in ("signal", "stop", "give_way", "mini_roundabout", "level_crossing", "crossing", "calming",
                          "pub_junction", "driveway", "trail")}
    for n, k in idx.items():
        t = tags.get(n, {})
        if t.get("highway") == "traffic_signals":
            ev["signal"].append(cum[k])
        if t.get("highway") == "stop":
            ev["stop"].append(cum[k])
        if t.get("highway") == "give_way":
            ev["give_way"].append(cum[k])
        if t.get("highway") == "mini_roundabout":
            ev["mini_roundabout"].append(cum[k])
        if t.get("railway") in ("level_crossing", "crossing"):
            ev["level_crossing"].append(cum[k])
        if t.get("highway") == "crossing":
            ev["crossing"].append(cum[k])
        if "traffic_calming" in t:
            ev["calming"].append(cum[k])
    names = []
    for wid, w in ways.items():
        if wid in own:
            continue
        hw, sv = w["tags"].get("highway"), w["tags"].get("service")
        touch = [n for n in w["nodes"] if n in idx]
        for n in set(touch):
            k = idx[n]
            names.append((float(cum[k]), hw, w["tags"].get("name") or w["tags"].get("ref") or ""))
            if hw in PUBLIC:
                ev["pub_junction"].append(cum[k])
            elif hw == "service":
                ev["driveway"].append(cum[k])
            elif hw in TRAIL:
                ev["trail"].append(cum[k])
    for kk in ev:
        ev[kk] = sorted(set(round(float(x), 1) for x in ev[kk]))
    km = L / 1000
    out["counts"] = {k: len(v) for k, v in ev.items()}
    out["per_km"] = {k: round(len(v) / km, 2) for k, v in ev.items()}
    hard = sorted(x for k in HARD for x in ev[k])
    def runs(points):
        p = [0.0] + sorted(points) + [L]
        gaps = np.diff(p)
        internal = gaps[1:-1] if len(gaps) > 2 else np.array([])
        return gaps, internal
    for name, pts in (("hard", hard), ("hard_or_public_junction", hard + ev["pub_junction"])):
        gaps, internal = runs(pts)
        out[f"runs_{name}"] = {"n_events": len(pts), "longest_between_events_m": float(internal.max()) if len(internal) else None,
                               "median_between_events_m": float(np.median(internal)) if len(internal) else None,
                               "longest_incl_ends_m": float(gaps.max()),
                               "share_len_in_runs_ge_1km": float(gaps[gaps >= 1000].sum() / L)}
    out["event_positions"] = ev
    out["side_ways"] = sorted(names)
    out["own_way_tags"] = {str(k): v["tags"] for k, v in own.items()}
    out["cum_m"] = cum.tolist()
    out["edge_speed_mph"] = [None if np.isnan(s) else float(s) for s in spd]
    return out
