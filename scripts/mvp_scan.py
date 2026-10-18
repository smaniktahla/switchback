"""MVP step 1: broadened geometry scan over the cached region ways -> data/mvp/stretches.pkl."""
import pickle
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, "src")
from switchback.discover import dedupe, merge_adjacent, scan

cfg = yaml.safe_load(open("config/mvp.yml"))
t = time.time()
res, long_ = scan("data/derived/scan_dc/region_ways.pkl", cfg)
print(f"{len(res)} raw stretches from {len(long_)} chains in {time.time()-t:.0f}s", flush=True)
keep = dedupe(merge_adjacent(res), cfg["discovery"]["dedupe_km"])
print(f"{len(keep)} after dedupe; km total {sum(r['length_m'] for r in keep)/1000:.0f}", flush=True)
Path("data/mvp").mkdir(exist_ok=True)
pickle.dump((keep, long_), open("data/mvp/stretches.pkl", "wb"))
