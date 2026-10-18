# Switchback


Phase 1: measure what makes a road enjoyable to ride, starting from roads riders rate highly.
Measurement and validation only — no route generation.

- `config/roads.yml` — reference roads as directed OSM node-to-node paths (edit to add roads)
- `data_in/ratings.csv` — human ratings, kept separate from measurements (blank until supplied)
- `config/sources.yml` — OSM extract provenance (sha256)
- `scripts/extract_reference.py` — M0: extract exact centerlines to `data/derived/<road>/`

Setup: `uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt`,
download the extracts listed in `config/sources.yml` into `data/raw/`.

Not for publication yet. `data/` is gitignored.

## Status
- M0 reference extraction, M1 geometry metrics, M2a topography (USGS 3DEP) done.
- M2b GraphHopper cross-check: inputs staged (`scripts/clip_osm.py`, `config/graphhopper/`), not yet run.
  Record: GraphHopper **11.1 release** computes curvature at import from per-edge OSM geometry (2D);
  `master` (12.0-SNAPSHOT) moved it to a post-build graph pass that uses 3D beeline. Compare against 11.1.

## MVP: find a road, plan a ride, export GPX
Open **http://10.10.10.226:8940** (user service `switchback`, AI2). Search or click a start point, browse ranked
roads within a radius, add roads to "My ride", Build route, Download GPX.
- `scripts/mvp_scan.py` -> `scripts/mvp_build.py` regenerate `app/data/candidates.json` (discovery bounds and default weights in `config/mvp.yml`; heuristics in `src/switchback/rank.py`).
- Coverage: VA/MD/WV within ~110 mi of DC (the cached Phase-1 region). Traffic from VDOT/SHA layers (WV: none). Unknown = neutral.
- Route = start -> chosen road (drawn from its own OSM geometry, so the GPX keeps it exactly) -> GraphHopper connector -> next road ... GraphHopper 11.1 runs on AI1 (`deploy/graphhopper/`, port 8989, profiles `car` = direct, `motorcycle` = twisty connectors).
- Visibility and live conditions are deliberately not part of the MVP.
