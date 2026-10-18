# Sight distance on the US-211 climb (first experiment, 2026-10-18)

Scope: the 4.8 km US-211 climb only, both directions. Visibility is measured separately from curvature and from temporary conditions (gravel, rain, potholes). It is a measurement of what a rider could see, **not** a safety rating and **not** a recommended speed.

## What is measured

Available sight distance (ASD) at every 5 m along the road, for a rider 1.7 m right of the centreline (lane centre of a 3.4 m lane), eyes 1.3 m above the road:

1. **Own-lane pavement**: how far ahead the rider can see a hazard-height (0.15 m) point of their own lane (gravel, debris, a stopped vehicle's base). Distance to the first point that is hidden; capped at 250 m.
2. **Opposing lane**: same, for a 1.0 m high target in the centre of the oncoming lane (a vehicle crossing the centreline).
3. **Corner exit and beyond the apex**: for each corner of 30 degrees or more, ASD at turn-in and at the apex, and whether the exit point is visible from each.

Obstructions: bare-earth terrain (USGS 3DEP, 1 m) alone, and terrain plus above-ground lidar returns (2014 NRCS Shenandoah point cloud, 5 non-ground points per m2, voxelised at 1 x 1 x 0.5 m; returns within 3 m of the eye ignored). Two voxel rules bracket the answer: **"any"** (one return makes an obstruction, includes thin branches, so a lower bound) and **"dense"** (two or more returns, closer to solid foliage and trunks). The stopping-distance lines on the charts are AASHTO-style reference values (2.5 s reaction, 3.4 m/s2 braking: 75 m at 35 mph, 110 m at 45 mph), shown for scale only.

## Results

| | terrain only | with lidar objects ("dense") | with lidar objects ("any") |
|---|---|---|---|
| Westbound (climb), median own-lane ASD | 147 m | 120 m | 95 m |
| Eastbound (descent), median own-lane ASD | 175 m | 120 m | 90 m |
| Westbound, share of road with ASD >= 35 mph reference | 96% | 89% | 76% |
| Westbound, share with ASD >= 45 mph reference | 79% | 63% | 46% |
| Eastbound, share with ASD >= 35 mph reference | 93% | 79% | 58% |
| Eastbound, share with ASD >= 45 mph reference | 72% | 46% | 30% |

- **Roadside objects matter more than terrain here.** Terrain alone flags 4-7 of the 20 corners as having a point where own-lane sight distance falls under 75 m; with lidar objects it is 10 (dense) to 15 (any) westbound and 14 to 17 eastbound.
- **Sight distance saw-tooths through the climb.** It shrinks as you approach each corner and jumps once you are past the visual obstruction (figure 1). So average ASD hides the moments that matter; the per-corner minimum is more informative (figure 2).
- **The exit of a corner is rarely visible from turn-in** (3 of 20 westbound, 5 of 20 eastbound) but usually from the apex (16 and 14 of 20). The own-lane view beyond the apex is typically 100-250 m.
- **Tight corners are the least visible.** Corners with minimum radius under 60 m average 58 m minimum own-lane ASD westbound against 88 m for wider ones (dense rule).
- **Opposing-lane visibility is worse than own-lane in left-handers westbound** (mean worst-case 60 m vs 87 m in right-handers); eastbound it is the right-handers (61 m vs 82 m).
- **Direction matters.** Eastbound (descent) has more corners with poor visibility than westbound (climb) under every rule.
- **Rider lane position changes little**: medians move by up to about 10 m between left, centre and right of the lane.

## Limits and checks still needed

- **The lidar is from 4 April 2014**: leaf-off and twelve years old. Summer foliage and regrowth will block more than the "dense" case; the "any" case is a rough stand-in, not a summer measurement.
- **Not validated against your experience yet.** The best test is whether the corners this flags as having poor sightlines are the ones that feel blind to you.
- **Geometry inputs are approximate**: OSM centreline accuracy of a few metres, a fixed lateral rider position, no lean angle or body position. Readings under 10 m (0-0.7% of positions with the dense rule, up to 4.5% with the any rule eastbound) are probably artifacts where the modelled lane touches an obstruction.
- **Lidar returns include guardrails, signs and vehicles present on the day**, treated as obstructions.
- Only this one road so far. Applying it to the other candidate stretches needs lidar tiles for each (hundreds of MB per area), so it is not yet automatic.

Files: `reports/sightdist/` (figures 1-3, `summary.csv`), data in `data/derived/asd/` (profiles and per-corner tables, not in git).
