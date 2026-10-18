# US-211 climb against look-alikes: traffic, speed, interruptions (2026-10-18)

Roads: the US-211 climb (reference) against Skyline Drive #1, US-211 east of New Market #19, and three candidates that fit the curve shape but are suspected false positives: Lake Braddock Drive #11, Park Central Road #13 and Beach Drive #18 (numbers are ranks in `reports/scan_dc/candidates.md`). Figure: `reports/context/fig1_context_comparison.png`. Full table: `comparison_derived.csv`. Source notes and limits: `feasibility.md`.

| | US-211 climb | Skyline Dr #1 | US-211 New Market #19 | Lake Braddock Dr #11 | Park Central Rd #13 | Beach Dr #18 |
|---|---|---|---|---|---|---|
| Length (km) | 4.9 | 8.6 | 4.5 | 3.5 | 3.0 | 6.0 |
| Speed tag | 35 mph | 35 mph | 55 mph | none | none | 25 mph |
| Traffic signals / stop signs | 0 / 0 | 0 / 0 | 0 / 0 | 2 / 0 | 0 / 0 | 3 / 3 |
| Marked crossings | 1 | 0 | 0 | 5 | 1 | 11 |
| Public side-road junctions | 1 | 0 | 7 | 9 | 3 | 7 |
| Longest run without signal/stop (m, lower bound) | 4,892 | 8,574 | 4,465 | 3,487 | 3,000 | 1,587 |
| Longest run also without a public junction (m) | 4,892 | 8,574 | 1,572 | 1,108 | 1,408 | 1,303 |
| Corners of 30 degrees or more per km | 4.2 | 4.1 | 2.3 | 3.0 | 3.5 | 2.9 |
| Longest chain of consecutive corners | 11 | 10 | 3 | 3 | 5 | 3 |
| Curved length above 0.3 g at the tagged limit | 27% | 16% | 71% | n/a | n/a | 0% |
| AADT (year, quality) | 2,200 (2025, F) | 800 (2024, O) | 6,000 (2025, G) | 2,100-11,000 (2025, G) | no count segment | 11,132 (SHA, year unstated) |
| Trucks / buses | 5.2% / 0.6% | n/a | 9.6% / 0.7% | 0.9% / 2.2% | n/a | 3.9% / n/a |
| Peak-hour flow, both directions (AADT x K) | 206 veh/h | n/a | 601 | 341 | n/a | 1,247 |
| Expected oncoming vehicles per ride (35 mph, average hour) | 4 | 3 | 10 | 3 | n/a | 25 |

## What the comparison shows

- **Sustained corner sequences separate the look-alikes most cleanly.** The US-211 climb (11 corners in the longest chain) and Skyline Drive (10) stand apart from every other road, whose longest chain is 3 to 5. Curve shape per window made them look alike; chaining shows the others are isolated bends.
- **Interruptions separate the false positives from the reference.** Beach Drive has 3 signals, 3 stop signs and 11 marked crossings in 6 km, and no uninterrupted run longer than 1.6 km. Lake Braddock Drive has 2 signals, 5 crossings and 9 public junctions in 3.5 km; its longest run clear of public junctions is 1.1 km. The US-211 climb has no signals or stops; its one counted public junction is the end node itself (the Thornton Gap junction), and one marked trail crossing sits at about 1.2 km. Skyline Drive has none.
- **At the tagged speed, Beach Drive's geometry asks very little**: 78% of its curved length stays under 0.1 g at 25 mph and none exceeds 0.3 g. Lake Braddock Drive and Park Central Road have no speed tag, so this cannot be checked for them.
- **US-211 near New Market looks like a partial match with a different character**: 55 mph limit, 71% of its curved length above 0.3 g at that limit (the posted speed is well above what the curves allow), 9.6% trucks, 6,000 vehicles a day, and 7 public junctions plus 8 driveways. Corner chains are short (3).
- **Traffic exposure is small on the climb**: about 2,200 vehicles a day and, at an average hour, about 4 oncoming vehicles over a ride. Beach Drive is about 11,000 a day and 25.
- **Weekday vs weekend** (where the weekday figure exists): Beach Drive is about 32% lighter at weekends and Lake Braddock Drive 30% lighter, a commuter signature. Not available for the climb.

## Limits

- Six roads is an illustration, not a validation. Nothing here has been checked against rides.
- **VDOT 2025 AADT means the 2025 estimate year**, mostly factored short-term counts, not a 2025 measurement of these exact segments. Maryland's figure has no stated year. Skyline Drive's count is from an outside source and covers 3 of its 5 segments.
- OSM driveway counts are unreliable. Speed tags have no source on the roads that have them. Unmapped signs and signals do not exist in these counts.
- Hourly, day-of-week and seasonal traffic are not measured; see `feasibility.md` for what can be estimated and what would need a data request.
- Visibility (sight distance) has only been computed for the US-211 climb and is not combined with anything here.
