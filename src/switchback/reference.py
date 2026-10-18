"""Extract a directed reference centerline between two OSM nodes.

Routes over the candidate ways only (respecting oneway), so the result is the
exact OSM geometry with no routing-engine involvement.
"""
import heapq
import json
import math
from pathlib import Path

import yaml

from .osm_ways import collect_ways

R = 6371008.8


def hav(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def build_graph(ways):
    adj, coords = {}, {}
    for w in ways.values():
        oneway = w["tags"].get("oneway") in ("yes", "true", "1")
        nodes = w["nodes"]
        for (a, ax, ay), (b, bx, by) in zip(nodes, nodes[1:]):
            if a == b:
                continue
            coords[a], coords[b] = (ax, ay), (bx, by)
            d = hav(ax, ay, bx, by)
            adj.setdefault(a, []).append((b, d, w["id"]))
            if not oneway:
                adj.setdefault(b, []).append((a, d, w["id"]))
    return adj, coords


def shortest_path(adj, src, dst):
    dist, prev, pq = {src: 0.0}, {}, [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == dst:
            break
        if d > dist.get(u, 1e18):
            continue
        for v, w, wid in adj.get(u, ()):
            nd = d + w
            if nd < dist.get(v, 1e18):
                dist[v], prev[v] = nd, (u, wid)
                heapq.heappush(pq, (nd, v))
    if dst not in prev and src != dst:
        raise ValueError(f"no path {src} -> {dst}")
    path, u = [dst], dst
    while u != src:
        u, wid = prev[u]
        path.append(u)
    return path[::-1], dist[dst]


def extract(road_id, cfg, raw_dir, out_dir):
    ways = collect_ways([Path(raw_dir) / f"{p}-latest.osm.pbf" for p in cfg["pbfs"]],
                        cfg["refs"], tuple(cfg["bbox"]), cfg.get("names", ()))
    adj, coords = build_graph(ways)
    path, length = shortest_path(adj, cfg["start_node"], cfg["end_node"])
    # which ways the path actually used, in order
    edge_way = {}
    for w in ways.values():
        for (a, _, _), (b, _, _) in zip(w["nodes"], w["nodes"][1:]):
            edge_way.setdefault((a, b), w["id"])
            edge_way.setdefault((b, a), w["id"])
    used = []
    for a, b in zip(path, path[1:]):
        wid = edge_way[(a, b)]
        if not used or used[-1] != wid:
            used.append(wid)
    way_tags = {wid: ways[wid]["tags"] for wid in used}
    keys = ["maxspeed", "surface", "lanes", "width", "lit", "bridge", "tunnel", "oneway", "highway", "name"]
    cum, dd = [0.0], 0.0
    for a, b in zip(path, path[1:]):
        dd += hav(*coords[a], *coords[b]); cum.append(dd)
    is_bridge = lambda tags: tags.get("bridge", "no") not in ("no", "") or tags.get("tunnel", "no") not in ("no", "")
    edge_br = [int(is_bridge(ways[edge_way[(a, b)]]["tags"])) for a, b in zip(path, path[1:])]
    node_br = [max(a, b) for a, b in zip([0] + edge_br, edge_br + [0])]   # a node on a bridge/tunnel edge
    meta = {
        "road_id": road_id, "length_m": length, "n_nodes": len(path), "ways_used": used,
        "attr_completeness": {k: sum(1 for t in way_tags.values() if k in t) / len(used) for k in keys},
        "way_tags": {str(k): v for k, v in way_tags.items()},
        "config": cfg,
    }
    out = Path(out_dir) / road_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    (out / "centerline_nodes.csv").write_text(
        "node_id,lon,lat,cum_m,deck\n" + "\n".join(
            f"{n},{coords[n][0]:.7f},{coords[n][1]:.7f},{c:.2f},{b}" for n, c, b in zip(path, cum, node_br)))
    (out / "centerline.geojson").write_text(json.dumps({
        "type": "Feature", "properties": {"road_id": road_id, "length_m": length},
        "geometry": {"type": "LineString", "coordinates": [list(coords[n]) for n in path]}}))
    return meta


def extract_sub(road_id, cfg, out_dir):
    """Sub-segment of an already-extracted road, cut at cumulative metres (snapped to a parent node)."""
    import pandas as pd
    out_dir = Path(out_dir)
    pd_ = pd.read_csv(out_dir / cfg["parent"] / "centerline_nodes.csv")
    i0 = int((pd_.cum_m - cfg.get("from_m", 0)).abs().idxmin())
    i1 = int((pd_.cum_m - cfg.get("to_m", pd_.cum_m.iloc[-1])).abs().idxmin())
    sub = pd_.iloc[i0:i1 + 1].copy()
    sub["cum_m"] -= sub.cum_m.iloc[0]
    out = out_dir / road_id
    out.mkdir(parents=True, exist_ok=True)
    sub.to_csv(out / "centerline_nodes.csv", index=False, float_format="%.7f")
    parent_meta = json.loads((out_dir / cfg["parent"] / "meta.json").read_text())
    meta = {"road_id": road_id, "parent": cfg["parent"], "length_m": float(sub.cum_m.iloc[-1]),
            "start_node": int(sub.node_id.iloc[0]), "end_node": int(sub.node_id.iloc[-1]),
            "n_nodes": len(sub), "ways_used": parent_meta["ways_used"],
            "attr_completeness": parent_meta["attr_completeness"],
            "way_tags": parent_meta["way_tags"], "config": cfg}
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    return meta


def load_roads(path="config/roads.yml"):
    return yaml.safe_load(open(path))["roads"]
