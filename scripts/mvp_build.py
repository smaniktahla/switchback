"""MVP step 2: enrich scanned stretches (interruptions, speed environment, corner chains, traffic) and write the
candidate file the app serves: app/data/candidates.json."""
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import requests
import yaml
from scipy.spatial import cKDTree

sys.path.insert(0, "src")
from switchback.discover import continue_road, corner_chains, merge_touching, stretch_nodes, way_graph
from switchback.rank import components, score
from switchback.roadctx import analyse, hav, read_context
from switchback.traffic import fetch_segments, join_road

cfg = yaml.safe_load(open("config/mvp.yml"))
PBF = {"VA": "data/mvp/virginia.osm.pbf", "MD": "data/mvp/maryland.osm.pbf", "WV": "data/mvp/west-virginia.osm.pbf"}
SHA = "https://mdgeodata.md.gov/imap/rest/services/Transportation/MD_AnnualAverageDailyTraffic/MapServer/1/query"
H = {"User-Agent": "Mozilla/5.0 switchback"}
COMPASS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
TDIR = Path("data/traffic"); TDIR.mkdir(exist_ok=True)


def traffic(i, road, state):
    """Median AADT along the stretch from the state layer's own values (VA layer = 2023, MD = 'current'); None if unavailable."""
    bb = (min(road["node_lon"]) - .004, min(road["node_lat"]) - .004, max(road["node_lon"]) + .004, max(road["node_lat"]) + .004)
    try:
        if state == "VA":
            segs = fetch_segments(bb, TDIR / f"mvp_va_{i}.json"); key = "ADT"
        elif state == "MD":
            f = TDIR / f"mvp_md_{i}.json"
            segs = json.load(open(f)) if f.exists() else requests.get(SHA, params={
                "f": "geojson", "where": "1=1", "geometry": ",".join(f"{v:.5f}" for v in bb), "geometryType": "esriGeometryEnvelope",
                "inSR": 4326, "outSR": 4326, "spatialRel": "esriSpatialRelIntersects", "outFields": "*", "returnGeometry": "true"},
                headers=H, timeout=90).json()
            json.dump(segs, open(f, "w")); key = "AADT"
        else:
            return None, 0.0
        _, assigned = join_road(road["node_lon"], road["node_lat"], segs)
        vals = [a[key] for a in assigned if a and a.get(key)]
        return (float(np.median(vals)) if vals else None), len(vals) / max(len(assigned), 1)
    except Exception as e:
        print(f"  traffic {i}: {str(e)[:80]}", flush=True)
        return None, 0.0


def main():
    stretches, chains = pickle.load(open("data/mvp/stretches.pkl", "rb"))
    region_ways, places = pickle.load(open("data/derived/scan_dc/region_ways.pkl", "rb"))
    places = [p for p in places if p[3] in ("city", "town", "village")]
    pk = np.array([[(p[1] + 77.04) * 86.8, (p[2] - 38.9) * 111.2] for p in places]); tree = cKDTree(pk)
    roads = []
    for i, s in enumerate(stretches):
        roads.append({**stretch_nodes(chains[s["chain_idx"]], s["lon"], s["lat"], s["s0"], s["s1"]), "state": s["state"]})
    n0 = len(stretches); stretches, roads = merge_touching(stretches, roads, ways=region_ways); print(f"merged {n0 - len(stretches)} touching stretches", flush=True)
    adj, loc = way_graph(region_ways, {s["road_key"] for s in stretches})
    ctx = {}
    for st, pbf in PBF.items():
        idx = [i for i, r in enumerate(roads) if r["state"] == st]
        if not idx:
            continue
        print(f"{st}: context for {len(idx)} stretches", flush=True)
        tags, ways = read_context(pbf, {n for i in idx for n in roads[i]["node_ids"]})
        for i in idx:
            ctx[i] = analyse(roads[i], tags, ways)
    out, fam_ids = [], {}
    for i, (s, r) in enumerate(zip(stretches, roads)):
        c = ctx[i]; cc = corner_chains(s["lon"], s["lat"])
        aadt, cov = traffic(i, r, s["state"])
        ev = c["event_positions"]; cum = np.array(c["cum_m"])
        hard = sorted(x for k in ("signal", "stop", "give_way", "mini_roundabout", "level_crossing") for x in ev[k])
        gl = np.array(r["node_lon"]); ga = np.array(r["node_lat"])
        pos = lambda m: [round(float(np.interp(m, cum, gl)), 5), round(float(np.interp(m, cum, ga)), 5)]
        names = {}
        for t in c["own_way_tags"].values():
            n = t.get("name") or t.get("ref")
            if n:
                names[n] = names.get(n, 0) + 1
        refs = {t.get("ref") for t in c["own_way_tags"].values() if t.get("ref")}
        fam = sorted(refs)[0] if refs else (max(names, key=names.get) if names else s["road_key"])
        fam_ids.setdefault(fam, set()).update(set(names) | refs)
        L = c["length_km"]
        mid = (r["node_lon"][len(gl) // 2], r["node_lat"][len(gl) // 2])
        mx, my = (mid[0] + 77.04) * 86.8, (mid[1] - 38.9) * 111.2
        d, j = tree.query([mx, my]); p = places[j]
        ang = (np.degrees(np.arctan2(mx - pk[j][0], my - pk[j][1])) + 360) % 360
        where = f"{d:.0f} km {COMPASS[int((ang + 22.5) // 45) % 8]} of {p[0]}" if d >= 1.5 else f"at {p[0]}"
        surf = {t.get("surface") for t in c["own_way_tags"].values() if t.get("surface")}
        m = {"deg_per_km": round(s["deg_per_km"]), "turns_per_km_45": round(s["turns_per_km_45"], 1), "radius_p50": round(s["radius_p50"]),
             "frac_straight": round(s["frac_straight"], 2), **cc,
             "hard_per_km": round(len(hard) / L, 2), "hard_events": {k: len(ev[k]) for k in ("signal", "stop", "give_way", "mini_roundabout", "level_crossing")},
             "pub_junctions_per_km": c["per_km"]["pub_junction"], "pub_junctions": c["counts"]["pub_junction"],
             "crossings": c["counts"]["crossing"], "longest_clear_m": round(c["runs_hard"]["longest_incl_ends_m"]),
             "speed_median_mph": c.get("speed_median_mph"), "speed_known_share": round(c["speed_known_share"], 2),
             "speed_mph_range": [min(v for v in c["edge_speed_mph"] if v) , max(v for v in c["edge_speed_mph"] if v)] if any(c["edge_speed_mph"]) else None,
             "aadt": aadt, "aadt_coverage": round(cov, 2), "length_km": round(L, 2)}
        comps = components(m)
        out.append({"id": i, "family": fam, "name": max(names, key=names.get) if names else s["road_key"], "ref": "/".join(sorted(refs)),
                    "highway": s["highway"], "state": s["state"],
                    "note": next((v for k, v in cfg.get("notes", {}).items() if k.lower() in (max(names, key=names.get) if names else s["road_key"]).lower()), ""), "where": where, "surface": "/".join(sorted(surf)) or "untagged (assumed paved)",
                    "metrics": m, "components": {k: round(v, 3) for k, v in comps.items()},
                    "score": round(score(comps, cfg["weights"]), 3),
                    "line": [[round(a, 5), round(b, 5)] for a, b in zip(r["node_lon"], r["node_lat"])],
                    "ext_end": continue_road(adj[s["road_key"]], loc, r["node_ids"], r["node_ids"][-1], r["node_ids"][-2]),
                    "ext_start": continue_road(adj[s["road_key"]], loc, r["node_ids"], r["node_ids"][0], r["node_ids"][1]),
                    "events": {"hard": [pos(x) for x in hard]}})
    out.sort(key=lambda x: -x["score"])
    # full geometry of roads that appear more than once, so consecutive pieces can be joined along the road itself
    count = {}
    for o in out:
        count[o["family"]] = count.get(o["family"], 0) + 1
    multi = {f: ids for f, ids in fam_ids.items() if count.get(f, 0) >= 2}
    roads_out = {f: [] for f in multi}
    for w in region_ways:
        for f, ids in multi.items():
            if w["ref"] in ids or w["name"] in ids:
                roads_out[f].append({"n": [p[0] for p in w["pts"]], "c": [[round(p[1], 5), round(p[2], 5)] for p in w["pts"]]})
    json.dump(roads_out, open("app/data/roads.json", "w"), separators=(",", ":"))
    print("road families with geometry:", {f: len(v) for f, v in roads_out.items()})
    Path("app/data").mkdir(parents=True, exist_ok=True)
    json.dump({"weights": cfg["weights"], "candidates": out, "coverage": "VA, MD, WV within ~110 mi of Washington DC; DC proper not scanned"},
              open("app/data/candidates.json", "w"), separators=(",", ":"))
    print(len(out), "candidates written;", "top:", [(o["name"], o["state"], o["score"]) for o in out[:8]])


main()
