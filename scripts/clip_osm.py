"""Clip all highway ways (and their nodes) inside each road's bbox into one small PBF for GraphHopper."""
import sys
from pathlib import Path

import osmium

sys.path.insert(0, "src")
from switchback.reference import load_roads

RAW, OUT = Path("data/raw"), Path("data/gh/clip.osm.pbf")


def inside(bb, lon, lat):
    return bb[0] <= lon <= bb[2] and bb[1] <= lat <= bb[3]


jobs = {}   # pbf name -> list of bboxes
for cfg in load_roads().values():
    for p in cfg.get("pbfs", []):
        jobs.setdefault(p, []).append(tuple(cfg["bbox"]))

way_ids, node_ids = {}, {}
for pbf, bbs in jobs.items():
    ws, ns = set(), set()
    fp = osmium.FileProcessor(str(RAW / f"{pbf}-latest.osm.pbf"), osmium.osm.NODE | osmium.osm.WAY).with_locations() \
        .with_filter(osmium.filter.KeyFilter("highway"))
    for w in fp:
        if not w.is_way():
            continue
        if any(n.location.valid() and inside(bb, n.location.lon, n.location.lat) for n in w.nodes for bb in bbs):
            ws.add(w.id); ns.update(n.ref for n in w.nodes)
    way_ids[pbf], node_ids[pbf] = ws, ns
    print(pbf, len(ws), "ways", len(ns), "nodes", flush=True)

OUT.unlink(missing_ok=True)
with osmium.SimpleWriter(str(OUT)) as wr:
    done = set()
    for pbf in jobs:
        for o in osmium.FileProcessor(str(RAW / f"{pbf}-latest.osm.pbf"), osmium.osm.NODE):
            if o.id in node_ids[pbf] and o.id not in done:
                wr.add_node(o); done.add(o.id)
    done = set()
    for pbf in jobs:
        for o in osmium.FileProcessor(str(RAW / f"{pbf}-latest.osm.pbf"), osmium.osm.WAY):
            if o.id in way_ids[pbf] and o.id not in done:
                wr.add_way(o); done.add(o.id)
print("wrote", OUT, OUT.stat().st_size // 1024, "KiB")
