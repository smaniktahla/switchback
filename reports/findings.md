# Switchback: first measurements (2026-10-18)

Roads: US-211 Sperryville to Thornton Gap (10.8 km, plus the 4.8 km climb from km 6), Tail of the Dragon (18 km), Cherohala Skyway (66.9 km, the section OSM names "Cherohala Skyway"; published length is ~43 mi, ours is 41.6 mi).
Baseline: 733 one-km windows on 94 other roads (trunk/primary/secondary/tertiary/unclassified) in the same OSM regions, i.e. mountain-heavy, not a random sample of US roads.
No ratings exist yet. Everything below is measurement unless it says "hypothesis". Figures are in `reports/figures/`.

## Measurements

| | US-211 full | US-211 climb | Dragon | Cherohala |
|---|---|---|---|---|
| heading change (deg/km) | 222 | 394 | **636** | 228 |
| turns >= 45 deg per km | 1.7 | 3.4 | **5.2** | 1.9 |
| median curve radius (m) | 173 | 144 | **94** | 183 |
| length with radius < 50 m | 2% | 5% | **17%** | 0% |
| share straight (R > 500 m) | 51% | 25% | 20% | 41% |
| longest straight (m) | 1210 | 110 | 150 | 870 |
| elevation gain / loss (m) | 451 / 3 | 297 / 0 | 204 / 521 | **1887 / 1349** |
| max sustained grade, 250 m | 7.2% | 7.2% | 5.9% | 10.0% |

- **Dragon is a different kind of road from the other three.** About 2.8x the heading change of the Cherohala or US-211 and the tightest radii. The Dragon-to-Cherohala ratio ranged 2.4-3.1x and Dragon-to-US-211 2.5-3.2x across 45 smoothing/resampling/threshold settings. Absolute values for the Dragon moved by up to ~40% (518-729 deg/km), the other roads by 15% or less.
- **Cherohala is not unusually curvy.** Its median window sits at the 68th percentile of ordinary windows in these regions; the Dragon is at the 96th, the US-211 climb the 87th, US-211 as a whole the 36th. Its curves are sweepers (median radius 183 m, none under 50 m).
- **What does set Cherohala and the Dragon apart is how long they stay twisty.** Longest unbroken run of 1 km windows at or above 150 deg/km: Dragon 17 km (all of it), Cherohala 18 km, US-211 climb 4 km. Only 27 of 110 ordinary road chains have a 4 km run at that level.
- **US-211's first ~6 km is nearly straight.** The twisty road you rate highly is the last ~4.8 km, a steady 5-8% climb with no flat spots (211 m up to 660 m).
- **Elevation does not track curve tightness** (rank correlation with grade: -0.07 to 0.37 depending on road).
- **The Dragon's marketed "318 curves in 11 miles" is not reproduced.** At a 15 deg threshold we count 8 turns/km (about 140 over the analyzed 17.4 km; 167 corners of any size). The total depends entirely on what counts as a curve.

## GraphHopper (version 11.1 release)

- Curvature = straight-line distance / length of an edge, 2D, between junction nodes. Stored in 4 bits (0.25-1.0, steps of 0.05). My recomputation from the route geometry matches its stored value exactly on every edge checked (100%); an independent recomputation from raw OSM junctions matched all edges it could map (US-211 100%, Dragon 100%, Cherohala 68%, the rest unexplained).
- **It cannot describe the Dragon.** The whole 18 km is 6 edges (median 2.0 km, longest 7.7 km), 78% of its length at the single value 0.5. US-211 is 50 edges and 48% "straight". The bundled `curvature.json` only penalizes values >= 0.98, so it cannot rank twistiness at all.
- Version note: `master` (12.0-SNAPSHOT) moved the calculation to a post-build 3D pass. Our numbers are for 11.1.
- Consequence for routing: GraphHopper is fine as the routing engine, but the twistiness score has to come from our own windowed measure (e.g. heading change per km), written back as an edge attribute.

## Data caveats

- Elevation (USGS 3DEP): 1 m and 10 m DEMs agree; a 30 m DEM inflates the Dragon's gain by ~50% and doubles p95 grade. Bare-earth DEMs also drop into the valley under bridges (the Cherohala viaduct read as a 40% grade); I interpolate across bridge decks.
- OSM node density differs by road (median vertex spacing 17.5 m on US-211 vs 7.6 m on the Dragon); smoothing (sigma 15 m) recovers radii down to ~30 m on synthetic arcs, and 1 m of random vertex noise can distort radii of a few hundred metres by 30% or more.
- Missing tags: Cherohala has maxspeed on 14% and lanes on 29% of its length. Surface is untagged on most "unclassified" roads, so paved vs gravel is unknown for them.

## Scan preview (hypothesis, not validated)

Ranking ordinary roads by their longest run at or above 150 deg/km, with no ratings used, puts **NC 28** (18 km run), **Skyline Drive** (11 km), Cades Cove Loop and Santeetlah Road (the Cherohala's continuation) near the top. NC 28 and Skyline Drive are well-known rider roads, which is encouraging but anecdotal. Several "unclassified" forest roads (River Road, Rafter Road) also rank high with no surface data, exactly the "twisty but unpleasant" case we cannot score yet.

## Ground truth and what it changes (added 2026-10-18)

Salil has ridden US-211 Sperryville to Thornton Gap many times and calls it his favorite short twisty hop in the DC Metro area. He has not ridden the Dragon, and has not ridden the Cherohala as far as we know, so those two are acclaimed but unrated for him: they are useful as other styles of road, not as targets for his taste.

- His one personal reference is **short**: the twisty part is the 4.8 km climb (394 deg/km, 3.4 turns >= 45 deg per km, median radius 144 m, 5% of length under 50 m, 25% straight, steady 6% grade, no flat spots). The "sustained length" idea above came from roads he has not ridden, so treat it as a hypothesis, not a requirement.
- A scan for his taste should therefore look for **3-10 km stretches near DC** that resemble the US-211 climb, with the Dragon and Cherohala as optional "different flavor" queries.
- The recorded rating for US-211 is notes-only (his words); no numeric score has been given, so none is entered.

## What would settle the next question

1. Ratings (rough 1-10) on a handful of roads he has ridden, including ones he does not like. Even 6-8 roads near DC would let us test which measures separate "favorite" from "twisty but meh".
2. A scan of VA/MD/WV around DC for short stretches matching the US-211 climb signature, filtered to paved public roads, producing a ranked list to ride and rate.
