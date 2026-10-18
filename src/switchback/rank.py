"""Transparent ranking heuristics for the MVP. Each component maps a measured value to 0..1 (1 = better for a
fun ride); the UI shows the raw value next to each component and recomputes the weighted mean live.
Nothing here is validated against rides: they are starting heuristics meant to be tuned by hand in config/mvp.yml."""
import math

import numpy as np

UNKNOWN = 0.5   # neutral score when a measurement is not available (e.g. WV traffic, untagged speed limits)


def _interp(x, xp, fp):
    return float(np.interp(x, xp, fp))


def twistiness(deg_per_km):                    # saturates at 500 deg/km (the US-211 climb is ~400-ish)
    return min(deg_per_km / 500.0, 1.0)


def corner_chain(longest_chain):               # chained corners (<= 100 m apart) make a "flow": 10+ is full marks
    return min(longest_chain / 10.0, 1.0)


def flow(hard_per_km, longest_clear_m, pub_junctions_per_km):
    """Interruptions: signals, stop/give-way signs, mini roundabouts, level crossings count hard; public side-road
    junctions count softly. 40% density of hard events, 40% longest clear run (3 km = full), 20% junction density."""
    a = math.exp(-2.0 * hard_per_km)
    b = min(longest_clear_m / 3000.0, 1.0)
    c = math.exp(-0.15 * pub_junctions_per_km)
    return 0.4 * a + 0.4 * b + 0.2 * c


def speed(median_mph):                         # 25 mph or less is a crawl; 40-50 is the sweet spot; 65 is highway-ish
    if median_mph is None:
        return UNKNOWN
    return _interp(median_mph, [15, 25, 35, 40, 50, 55, 65], [0.05, 0.3, 0.8, 1.0, 1.0, 0.7, 0.3])


def traffic(aadt):                             # informational: lower is better; unknown is neutral
    if aadt is None:
        return UNKNOWN
    return _interp(aadt, [500, 2000, 5000, 10000, 20000], [1.0, 0.85, 0.5, 0.2, 0.0])


def length(km):                                # 6-12 km is a good stretch; very short ones are hardly worth routing to
    return _interp(km, [3, 4, 6, 12, 20], [0.4, 0.8, 1.0, 1.0, 0.7])


def components(c):
    return {"twistiness": twistiness(c["deg_per_km"]), "corner_chain": corner_chain(c["longest_corner_chain"]),
            "flow": flow(c["hard_per_km"], c["longest_clear_m"], c["pub_junctions_per_km"]),
            "speed": speed(c["speed_median_mph"]), "traffic": traffic(c["aadt"]), "length": length(c["length_km"])}


def score(comps, weights):
    tw = sum(weights.values())
    return sum(weights[k] * comps[k] for k in weights) / tw
