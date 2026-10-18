# Traffic, speed environment and interruptions: data-source feasibility (2026-10-18)

Each dimension below is measured separately from geometry (curvature, corner sequences) and visibility (sight distance), and from current conditions (weather, gravel, live traffic). Nothing is combined into a score.

## 1. Traffic volume

| Source | What it gives | Verified now | Limits |
|---|---|---|---|
| **VDOT AADT 2025** (per-county spreadsheets, "AADT 2025 <County>" on data.virginia.gov, catalog entries updated 2026-08-07) | Average annual daily traffic (both directions), AADT quality code, vehicle mix (4-tire, bus, single-unit trucks 2-axle and 3+ axle, combination trucks), K factor (design-hour share), direction factor, weekday AADT, a nominal date | Downloaded Rappahannock, Page, Madison, Shenandoah and Fairfax counties. Every one of the 5 road segments we needed had a 2025 row | No geometry in the spreadsheet. The "data date" is 1 January of the estimate year, not the day a count was taken. Most values are factored short-term counts |
| **VDOT traffic volume feature service** (ArcGIS, `VDOT_Bidirectional_Traffic_Volume`) | Geometry for the same segments, with the same fields | Join key `LINKID` equals the spreadsheet's `Link ID`: 100% of segments on our roads matched (3 of 5 on Skyline Drive, which VDOT lists as VA-48, 108 of 108 near Lake Braddock Drive, 9 of 9, 4 of 4) | Its attribute values are the **2023** estimates (metadata still says "1986 to 2022"). Use it for geometry only, take 2025 values from the spreadsheets |
| **MDOT SHA AADT** (ArcGIS MapServer `MD_AnnualAverageDailyTraffic`, layer 1, on `mdgeodata.md.gov`) | AADT, weekday AADT, K, D factors, counted-or-factored flag, and a vehicle-class split that includes motorcycles | Beach Drive (MD): 11,132 vehicles a day, 3.9% trucks, 1.0% motorcycles | The annual columns end at 2018 and the "current" value has no stated year. `geodata.md.gov` returned a maintenance page during testing; `mdgeodata.md.gov` worked. No count segment exists for Park Central Road |
| West Virginia | Not investigated | | |

**Spatial join (works):** sample the OSM road every 10 m; for each sample take the nearest count segment within 25 m whose direction is within 30 degrees of the road; then summarize by length. Count segments for a bidirectional road appear once per direction, so duplicates are dropped by `Link ID`.

**Quality codes (from the layer description):** A and B are continuous counters (best); F factored short-term count; G factored short-term count with a growth element; H historical estimate; M manual estimate; N borrowed from a neighbouring link; O supplied by an outside source; R unfactored 24-hour count; T ITE trip-generation estimate; X not available. 61,722 segments carry a code "V" that the description does not define, so treat V as low confidence. Our roads: US-211 climb F, Skyline Drive O, Lake Braddock Drive G, US-211 near New Market G.

**Coverage and confidence in practice:** the 2025 spreadsheets cover Interstates, primary and arterial routes and many secondary county roads. Skyline Drive's 800 vehicles a day is an outside-source figure, probably National Park Service entrance data. Skyline Drive is a federal park road and Beach Drive is a park/government road (SHA prefix GV), so a state figure may not describe the whole road.

**Keep average traffic apart from live traffic:** AADT is an annual average. Peak-hour flow is estimated as AADT times K, and expected oncoming vehicles per ride is computed from AADT, a 50/50 directional split and an assumed pace. None of this says anything about a given Saturday.

## 2. Time-dependent traffic (hour, weekday/weekend, season)

| Question | Feasible now | How |
|---|---|---|
| Weekday vs weekend pattern | Partly | Compare weekday AADT with all-days AADT: weekend-day traffic = (7 x AADT - 5 x weekday) / 2. Beach Drive comes out about 32% lighter at weekends (commuter pattern); US-211 near New Market shows no difference; the US-211 climb has no weekday figure in the 2025 file |
| Hour of day | Roughly | K factor (share of daily traffic in the peak hour) and direction factor are in the file. A full hourly curve needs continuous-counter data. VDOT's counts page lists no hourly download and gives vdot.tms@vdot.virginia.gov for data requests; the P4P platform (vdotp4p.com) was not examined |
| Season | Proxy only | Shenandoah National Park monthly visitation is public (NPS IRMA stats) and tracks Skyline Drive / Thornton Gap use, with October the peak historically. Not a traffic count |
| Typical conditions by hour from vehicle speeds | Not free | Commercial probe-speed data (INRIX, HERE, TomTom, StreetLight), or the federal NPMRDS speed data (restricted to agencies). Not purchased and not planned |

Recommended next step if this dimension turns out to matter: request hourly data for the two or three continuous-count stations nearest the roads we care about, and build weekday/weekend and monthly profiles by road type, labelled as estimates.

## 3. Speed environment (OpenStreetMap)

- **Tags read:** `maxspeed`, `maxspeed:type`, `source:maxspeed`. Categories: posted (type or source says sign or survey), legal default (an implicit or `US:` type), tagged with no source, missing. Missing values are **not** filled with a state default.
- **Current coverage on these roads:** US-211 climb, Skyline Drive, Beach Drive and US-211 near New Market have a speed tag (35, 35, 25 and 55 mph) but with no source, so none can be called "posted" with certainty. Lake Braddock Drive and Park Central Road have no speed tag.
- **Lawful-speed geometry:** for each curved sample, lateral acceleration at the tagged limit = speed squared x curvature / g. Reported as the share of curved length in bands (under 0.1 g, 0.1-0.3, 0.3-0.5, over 0.5). This rewards engaging geometry at the limit, not high limits. It describes how demanding the corners are at that speed; it is not a recommended speed.

## 4. Uninterrupted Riding Potential (components only)

Measured from OSM node tags and the ways that touch the road: traffic signals, stop and give-way signs, mini-roundabouts, level crossings, marked crossings, junctions with public roads, junctions with service/driveway ways and with trails, then the distance between interruptions. Plus sustained corner sequences from the geometry analysis and the traffic dimension above.

Confidence: signals and stops are mapped well in OSM; **driveway counts are not reliable** (they are often unmapped; US-211 near New Market shows 8, the US-211 climb shows 0 where houses may be unmapped). Public junctions are better. No score is built from these components yet.
