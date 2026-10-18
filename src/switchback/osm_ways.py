"""Pull candidate road ways (by ref tag, inside a bbox) out of OSM PBF extracts.

Keeps the node-id list per way so ways can be stitched topologically later,
independent of any routing engine.
"""
import json
import osmium


class _Collector(osmium.SimpleHandler):
    def __init__(self, ref_patterns, bbox, names=()):
        super().__init__()
        self.refs = ref_patterns
        self.names = set(names)
        self.min_lon, self.min_lat, self.max_lon, self.max_lat = bbox
        self.ways = {}

    def way(self, w):
        if "highway" not in w.tags:
            return
        ref = w.tags.get("ref", "")
        parts = [p.strip() for p in ref.replace(",", ";").split(";")]
        if not any(p in self.refs for p in parts) and w.tags.get("name", "") not in self.names:
            return
        nodes = []
        for n in w.nodes:
            if not n.location.valid():
                return
            nodes.append((n.ref, n.location.lon, n.location.lat))
        if not any(self.min_lon <= x <= self.max_lon and self.min_lat <= y <= self.max_lat
                   for _, x, y in nodes):
            return
        self.ways[w.id] = {
            "id": w.id,
            "nodes": nodes,
            "tags": {k: v for k, v in w.tags},
            "version": w.version,
        }


def collect_ways(pbf_paths, ref_patterns, bbox, names=()):
    """Union of matching ways across extracts (border ways can appear in both)."""
    out = {}
    for p in pbf_paths:
        c = _Collector(set(ref_patterns), bbox, names)
        c.apply_file(str(p), locations=True)
        out.update(c.ways)
    return out


def dump_json(ways, path):
    with open(path, "w") as f:
        json.dump(list(ways.values()), f)
