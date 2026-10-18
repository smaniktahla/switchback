# Ride feedback: how rides should feed back into Switchback

Status: design for review. Only the templates exist; nothing is wired into the analysis yet. The aim is to test each measured dimension against what a rider actually experienced without letting a few rides rewrite the model.

## Principles

1. **Separate dimensions, separate answers.** Flow/engagement, visibility, interruptions, traffic, pavement and overall enjoyment are rated independently. A rider can love a road whose traffic was bad that day.
2. **Persistent vs transient.** Every observation is tagged either a property of the road (a blind corner, a signal, a pinch point) or a condition of that ride (wet, gravel after a storm, a slow truck, fog, leaf-on foliage, sun glare). Transient items never change a road's measurements; they only qualify how much weight a ride's ratings get for the relevant dimension.
3. **Rate after, not during.** Capture takes about five minutes at the end of the ride (or by voice note afterwards). Nothing requires the rider to look at a screen on the road.
4. **Small numbers are treated as small.** No weights, thresholds or models are fitted until there are enough independent observations (a first target: 30 or more rated corners across at least 6 roads, and 8 or more rides). Until then the feedback is used to check and to generate hypotheses, not to tune.
5. **Hold out whole roads** when testing anything fitted to feedback.
6. **Private by default.** Real ride data lives in `data_private/` (git-ignored); only the empty templates are tracked, because the repository may become public.

## What gets recorded

**Ride level** (`ride_log.csv`, one row per ride): road and direction, date and start time, pace intention (relaxed / brisk / spirited), bike, dry or wet, temperature band, leaf state (bare / leaf-on), traffic encountered vs expected (lighter / as expected / heavier) with numbers of oncoming vehicles if remembered, and overall enjoyment (1-10).

**Marks** (`ride_marks.csv`, many rows per ride), each tied to a place by either a corner number from the report figures (for example "westbound corner 7"), a distance from the start, or a lat/lon from the GPX track:

| Mark type | Meaning | Default class |
|---|---|---|
| `blind_corner` | could not see enough through it to judge hazards, oncoming traffic or the exit | persistent |
| `clear_corner` | could see well through it | persistent |
| `great_flow` / `awkward_flow` | corner or sequence that flowed well or badly | persistent |
| `surprise` | tightening radius, off-camber, crest or other unexpected geometry | persistent |
| `interruption` | signal, stop, junction or driveway activity that broke the flow | persistent if structural, transient if a one-off |
| `pavement` | surface quality good or bad | persistent unless clearly a one-off |
| `hazard` | gravel, debris, animal, stopped vehicle, water | transient |
| `traffic_event` | slow vehicle, group of cars, event traffic | transient |

Each mark carries a 1-5 intensity, a persistent/transient flag the rider can override, and a free-text note.

**Road or section level** (the existing `ratings.csv`, keeping its separate columns): overall, flow, technical challenge, scenery and pavement, plus traffic conditions on the day.

## How it is compared with the measurements

- **Visibility:** for each corner the rider marked clear or blind, compare with the model's minimum own-lane and opposing-lane sight distance. Report agreement (how many marked-blind corners the model also flags, and how many flagged corners the rider did not mark) and the rank correlation between rider scores and model distances. Wet or foggy rides are excluded from this check.
- **Interruptions and traffic:** compare the interruptions the rider reports with those found in OpenStreetMap (missing signals and driveways are expected findings, and each one is logged as a map-data gap) and compare reported traffic with the count-based expectation.
- **Flow / geometry:** compare great and awkward flow marks and the flow score with corner chains, lateral demand at the tagged speed, and radius sequences.
- **Overall enjoyment:** rank correlation with each dimension separately. A combined score is considered only once enough roads exist, validated on held-out roads, and disclosed as exploratory.
- **Disagreements are the product.** Every case where model and rider disagree is written up as a hypothesis (for example "stone wall inside the bend is not in the lidar") before anything is changed.

## Pilot

Ride the US-211 climb in both directions and one or two candidates from the DC list, with the sheet filled in afterwards. That gives about 40 corners and a first agreement check. Review the sheet itself after the pilot: if a question was hard to answer or felt like noise, cut it.

## Files

- `data_in/ride_log.csv` and `data_in/ride_marks.csv`: empty, tracked templates.
- `data_private/`: git-ignored; copy the templates here and fill them in.
