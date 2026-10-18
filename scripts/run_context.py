"""Context comparison: speed environment, interruptions/URP components, traffic, corner sequences.
Each dimension is reported separately; nothing here is combined into a score."""
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from scipy.spatial import cKDTree

sys.path.insert(0, "src")
from switchback.geometry import Params, build_series, segment
from switchback.roadctx import analyse, hav, read_context
from switchback.traffic import fetch_segments, join_road, load_county_xlsx

D, OUT = Path("data/derived/context"), Path("reports/context")
P = Params()
roads = pickle.load(open(D / "roads.pkl", "rb"))
SHA = "https://mdgeodata.md.gov/imap/rest/services/Transportation/MD_AnnualAverageDailyTraffic/MapServer/1/query"
H = {"User-Agent": "Mozilla/5.0 switchback-research"}


def osm_context():
    f = D / "osm_context.pkl"
    if f.exists():
        return pickle.load(open(f, "rb"))
    res = {}
    for st, pbf in (("VA", "data/raw/virginia-latest.osm.pbf"), ("MD", "data/raw/maryland-latest.osm.pbf")):
        names = [k for k, v in roads.items() if v["state"] == st]
        tags, ways = read_context(pbf, set(i for k in names for i in roads[k]["node_ids"]))
        for k in names:
            res[k] = analyse(roads[k], tags, ways)
    pickle.dump(res, open(f, "wb"))
    return res


def corner_and_lateral(road, ctx):
    ser = build_series(road["lon"], road["lat"], P)
    corners, _ = segment(ser, P)
    c = corners[(~corners.partial) & (corners.angle_deg >= 30)].sort_values("s_start")
    km = float(ser.step[ser.valid].sum()) / 1000
    out = {"geom_km": km, "corners_30deg_per_km": len(c) / km}
    chains, cur = [], 1
    for g in (c.s_start.values[1:] - c.s_end.values[:-1]):
        if g <= 100:
            cur += 1
        else:
            chains.append(cur); cur = 1
    if len(c):
        chains.append(cur)
    out["longest_corner_chain"] = int(max(chains)) if chains else 0
    out["share_corners_in_chains_ge5"] = float(sum(x for x in chains if x >= 5) / max(len(c), 1))
    # lateral acceleration at the tagged limit
    nlon, nlat = np.array(road["node_lon"]), np.array(road["node_lat"])
    kd = cKDTree(np.c_[(nlon - nlon[0]) * 86800, (nlat - nlat[0]) * 111200])
    v = ser[ser.valid]
    _, nk = kd.query(np.c_[(v.lon.values - nlon[0]) * 86800, (v.lat.values - nlat[0]) * 111200])
    sp = np.array([np.nan if s is None else s for s in ctx["edge_speed_mph"]])
    mph = sp[np.minimum(nk, len(sp) - 1)]
    curved = np.abs(v.kappa.values) > 1 / P.r_straight
    a = (mph * 0.44704) ** 2 * np.abs(v.kappa.values) / 9.81
    ok = curved & ~np.isnan(a)
    out["lat_speed_known_share_of_curves"] = float(ok.sum() / max(curved.sum(), 1))
    if ok.any():
        for lo, hi, nm in ((0, .1, "lt0.1g"), (.1, .3, "0.1_0.3g"), (.3, .5, "0.3_0.5g"), (.5, 9, "gt0.5g")):
            out[f"lat_share_{nm}"] = float(((a >= lo) & (a < hi))[ok].sum() / ok.sum())
        out["lat_p95_g"] = float(np.percentile(a[ok], 95))
    return out


def vdot(road, name):
    bb = (min(road["lon"]) - .004, min(road["lat"]) - .004, max(road["lon"]) + .004, max(road["lat"]) + .004)
    segs = fetch_segments(bb, f"data/traffic/vdot_{name}.json")
    x25 = pd.concat([load_county_xlsx(p) for p in Path("data/traffic").glob("aadt2025_*.xlsx")]).drop_duplicates("link_id").set_index("link_id")
    ps, assigned = join_road(road["lon"], road["lat"], segs)
    rows = []
    for a in assigned:
        if a is None:
            rows.append(None); continue
        lid = int(float(a["LINKID"]))
        if lid in x25.index:
            r = x25.loc[lid]; rows.append(dict(src="2025 spreadsheet", year=2025, aadt=r.aadt, q=r.aadt_q, aawdt=r.aawdt, k=r.k, dirf=r.dir_factor,
                                                trucks=100 * sum(float(r[c] or 0) for c in ("pct_su2", "pct_su3", "pct_comb1", "pct_comb2")), bus=100 * float(r.pct_bus or 0), date=str(r.data_date)[:10],
                                                label=f"{a['ROUTE_COMMON_NAME']}: {a['START_LABEL']} -> {a['END_LABEL']}"))
        else:
            rows.append(dict(src="layer (older)", year=pd.to_datetime(a["DATA_DATE"], unit="ms").year, aadt=a["ADT"], q=a["ADT_QUALITY"], aawdt=a["AAWDT"],
                             k=a["K_FACTOR"], dirf=a["DIRECTION_FACTOR"], trucks=sum(float(a[c] or 0) for c in ("PERCENT_TRUCK_2_AXLE", "PERCENT_TRUCK_3_AXLE", "PERCENT_TRUCK_1_TRAIL", "PERCENT_TRUCK_2_TRAIL")),
                             bus=float(a["PERCENT_BUS"] or 0), date=str(pd.to_datetime(a["DATA_DATE"], unit="ms").date()), label=f"{a['ROUTE_COMMON_NAME']}: {a['START_LABEL']} -> {a['END_LABEL']}"))
    cov = [r for r in rows if r]
    out = {"traffic_source": "VDOT", "traffic_coverage": len(cov) / len(rows)}
    if cov:
        df = pd.DataFrame(cov)
        out.update(aadt_median=float(df.aadt.median()), aadt_min=float(df.aadt.min()), aadt_max=float(df.aadt.max()), year=int(df.year.max()),
                   quality="/".join(sorted(set(df.q.astype(str)))), aawdt_median=float(df.aawdt.astype(float).median()),
                   k_median=float(df.k.astype(float).median()), dir_median=float(df.dirf.astype(float).median()),
                   trucks_pct=float(df.trucks.astype(float).median()), bus_pct=float(df.bus.astype(float).median()),
                   count_dates=f"{df.date.min()} to {df.date.max()}", segments="; ".join(sorted(set(df.label)))[:160])
    return out


def sha(road, name):
    bb = (min(road["lon"]) - .003, min(road["lat"]) - .003, max(road["lon"]) + .003, max(road["lat"]) + .003)
    f = Path(f"data/traffic/sha_{name}.geojson")
    segs = json.load(open(f)) if f.exists() else requests.get(SHA, params={"f": "geojson", "where": "1=1", "geometry": ",".join(f"{v:.5f}" for v in bb), "geometryType": "esriGeometryEnvelope", "inSR": 4326, "outSR": 4326, "spatialRel": "esriSpatialRelIntersects", "outFields": "*", "returnGeometry": "true"}, headers=H, timeout=90).json()
    ps, assigned = join_road(road["lon"], road["lat"], segs)
    cov = [a for a in assigned if a]
    out = {"traffic_source": "MDOT SHA", "traffic_coverage": len(cov) / len(assigned)}
    if cov:
        df = pd.DataFrame(cov)
        out.update(aadt_median=float(df.AADT.median()), aadt_min=float(df.AADT.min()), aadt_max=float(df.AADT.max()), year=None,
                   quality="/".join(sorted(set(df.COUNTED_FACTORED.astype(str)))), aawdt_median=float(df.AAWDT.astype(float).median()),
                   k_median=float(df.K_FACTOR.astype(float).median()) / 100, dir_median=float(df.D_FACTOR.astype(float).median()) / 100,
                   trucks_pct=float(df.TRUCK_AADT_PCT_OVERALL.astype(float).median() * 100) if df.TRUCK_AADT_PCT_OVERALL.notna().any() else None,
                   segments="; ".join(sorted(set(df.ROADNAME.astype(str))))[:160])
    return out


def main():
    ctx = osm_context()
    rows = []
    for name, road in roads.items():
        c = ctx[name]; r = {"road": name, "state": road["state"], "length_km": round(c["length_km"], 2)}
        r.update(corner_and_lateral(road, c))
        r.update({"speed_known": c["speed_known_share"], "speed_median_mph": c.get("speed_median_mph"), "speed_categories": json.dumps(c["speed_category_share"]),
                  "speed_changes_per_km": c.get("speed_changes_per_km")})
        r.update({f"per_km_{k}": v for k, v in c["per_km"].items()})
        r.update({f"count_{k}": v for k, v in c["counts"].items()})
        for nm in ("hard", "hard_or_public_junction"):
            rr = c[f"runs_{nm}"]
            r[f"run_{nm}_longest_incl_ends_m"] = rr["longest_incl_ends_m"]; r[f"run_{nm}_median_internal_m"] = rr["median_between_events_m"]
            r[f"run_{nm}_share_len_ge_1km"] = rr["share_len_in_runs_ge_1km"]
        key = name.split()[0].lower() + "_" + str(road["rank"])
        try:
            r.update(vdot(road, key) if road["state"] == "VA" else sha(road, key))
        except Exception as e:
            r["traffic_error"] = str(e)[:80]
        rows.append(r)
    df = pd.DataFrame(rows); df.to_csv(OUT / "comparison.csv", index=False)
    pd.set_option("display.width", 250, "display.max_columns", 40)
    print(df.set_index("road")[["length_km", "corners_30deg_per_km", "longest_corner_chain", "speed_median_mph", "speed_known", "per_km_signal", "per_km_stop",
                                 "per_km_pub_junction", "per_km_driveway", "run_hard_longest_incl_ends_m", "run_hard_or_public_junction_longest_incl_ends_m",
                                 "lat_share_gt0.5g", "traffic_coverage", "aadt_median", "year"]].round(2).T.to_string())


if __name__ == "__main__":
    main()
