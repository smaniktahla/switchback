import sys
sys.path.insert(0, "src")
from switchback.reference import extract, extract_sub, load_roads

roads = load_roads()
for rid, cfg in roads.items():
    if "parent" in cfg:
        continue
    m = extract(rid, cfg, "data/raw", "data/derived")
    print(f"{rid}: {m['length_m']:.0f} m ({m['length_m']/1609.344:.2f} mi), {m['n_nodes']} nodes, {len(m['ways_used'])} ways")
for rid, cfg in roads.items():
    if "parent" in cfg:
        m = extract_sub(rid, cfg, "data/derived")
        print(f"{rid}: {m['length_m']:.0f} m from node {m['start_node']} (parent {m['parent']})")
