<p align="center"><img src="app/static/logo.png" alt="Switchback" width="320"></p>

# 🏍️ Switchback

### Less highway. More corners.

**Switchback is an open-source motorcycle route discovery and planning tool that helps you find great riding roads, connect them into a ride, and export the route as GPX.**

There are a LOT of motorcycle and driver-focused route-planning tools out there these days. But we're taking a different approach:

Find the twisties for you. Then you put them all together how you want.

It analyzes real road geometry, sustained corner sequences, intersections, speed limits, and available traffic data to identify roads that offer engaging, uninterrupted riding.

**Find the curves. Build the ride. Enjoy the road.**

---

## What Switchback does

### 🏔️ Discover great riding roads

Explore roads ranked by motorcycle-friendly characteristics rather than simply distance or travel time.

Switchback considers:

- **Twistiness:** How much a road bends, including corner frequency and curve geometry.
- **Corner sequences:** Sustained stretches of engaging curves rather than isolated bends.
- **Flow:** Traffic signals, junctions, and other interruptions that break the rhythm.
- **Speed environment:** Whether the geometry is engaging at normal, lawful riding speeds.
- **Traffic:** Available historical traffic-volume estimates.
- **Ride length:** How much continuous interesting road is available.

Ranking preferences can be adjusted to favor the kind of riding you enjoy.

### 🗺️ Plan your ride

Use the interactive map to find interesting stretches of road, add them to your ride, and connect them into a complete journey.

Switchback uses GraphHopper to calculate connecting routes while preserving the geometry of the roads you've selected.

### 📍 Export GPX

Download the completed ride as a GPX track for use with compatible motorcycle navigation applications.

Unlike a simple list of destination waypoints, the exported track retains the intended road geometry.

### 🔧 Self-hosted and open source

Switchback uses OpenStreetMap data, Python-based road analysis, and GraphHopper routing.

The application is designed for self-hosting, without requiring a commercial motorcycle-route subscription.

---

## Screenshots

*Application screenshots coming soon.*

Suggested screenshots:

- Interactive road-discovery map
- Road rankings and adjustable preferences
- Selected roads and completed ride
- GPX export

---

## How it works

Switchback separates discovering a great road from planning how to reach it.

**1. Analyze the roads**

OpenStreetMap geometry is processed to identify curves, corner sequences, straightaways, and road characteristics.

**2. Rank the candidates**

Configurable heuristics evaluate twistiness, corner continuity, interruptions, speed environment, traffic estimates, and segment length.

**3. Build a route**

Choose the roads you want to ride. GraphHopper connects them into a navigable journey.

**4. Export and ride**

Download the planned route as GPX and open it in a compatible navigation application.

The ranking system uses transparent heuristics—not a machine-learning model claiming to know which roads are objectively best.

---

## Current status

**Early MVP — under active development**

Implemented:

- Road discovery using OpenStreetMap geometry
- Adjustable ranking weights
- Sustained-corner and interruption analysis
- Available speed-limit and historical traffic context
- Interactive map-based route selection
- GraphHopper-powered route connections
- GPX track export

### Current geographic coverage

The initial dataset covers selected roads in Virginia, Maryland, and West Virginia, within approximately 110 miles of Washington, DC.

This is a geographically limited prototype, not yet a nationwide routing service.

### Known limitations

- Road rankings are experimental and have not been broadly validated against rider experience.
- Traffic information is historical, not live.
- Road-surface tags may be missing or incomplete.
- Weather, current pavement hazards, and live incident reports are not integrated.
- GPX track-following behavior depends on the navigation application used.
- Route travel-time estimates are approximate.

Switchback does not determine safe cornering speeds or guarantee road conditions.

---

## Running Switchback

Switchback currently consists of two primary components:

**Switchback application**

A lightweight Python HTTP server providing the interactive map, candidate-road data, route-building endpoints, and GPX export.

**GraphHopper routing engine**

An independently deployed routing service used to connect selected road segments.

### Requirements

- Python and the dependencies in `requirements.txt`
- Generated Switchback candidate data
- A running GraphHopper instance with compatible routing profiles
- OpenStreetMap extracts for rebuilding road datasets

### Launch the application

Once dependencies, candidate data, and GraphHopper are configured:

```bash
export SWITCHBACK_GH=http://localhost:8989
python app/server.py
```

Open:

`http://localhost:8940`

The port can be changed using `SWITCHBACK_PORT`.

**Note:** This is the application launch procedure, not a complete clean-install guide. Preparing the OSM data and GraphHopper graph is currently a separate setup process.

### Customizing discovery and ranking

Edit `config/mvp.yml` to change discovery filters and the default ranking weights.

The associated ranking implementation lives in `src/switchback/rank.py`.

Dataset generation uses:

```bash
python scripts/mvp_scan.py
python scripts/mvp_build.py
```

These scripts require the applicable regional OSM extracts and intermediate datasets.

---

## Technology

| Component | Technology |
|---|---|
| Road data | OpenStreetMap |
| Routing | GraphHopper |
| Analysis | Python, NumPy, SciPy |
| Geographic processing | PyOsmium and related tools |
| Backend | Python standard-library HTTP server |
| Export | GPX 1.1 |
| Deployment | Self-hosted |

Additional research tooling supports elevation, curvature, visibility, and traffic analysis.

---

## Road research

Switchback began with a simple question:

*What makes a motorcycle road genuinely enjoyable?*

Initial research compared roads including US-211 at Thornton Gap, Tail of the Dragon, and Cherohala Skyway.

The analysis revealed an important distinction: a road can contain plenty of curves without providing a sustained, enjoyable riding experience.

This led to a stronger emphasis on **continuous corner sequences, fewer interruptions, and engaging road geometry**.

The original research and measurement code remain available in the repository for further experimentation.

---

## Roadmap

Potential future improvements include:

- Broader geographic coverage
- Better road-surface and pavement-condition information
- Weather-aware ride planning
- More detailed rider visibility analysis
- Improved time-dependent traffic estimates
- Rider feedback and personalized ranking
- Additional navigation and export options

Features will be prioritized based on real-world usefulness rather than research complexity.

---

## Contributing

Contributions, testing, and feedback are welcome.

Particularly valuable contributions include regional road-data improvements, reproducible bug reports, GPX compatibility testing, and feedback from riders familiar with recommended routes.

See the repository's issues for current development discussions.

---

## Data and safety

Switchback relies on OpenStreetMap and other geographic datasets whose completeness and accuracy vary.

Suggested roads may contain hazards, poor surfaces, closures, wildlife, or unexpected traffic.

Always observe applicable laws, ride within sight distance and conditions, and verify the route before setting out.

---

**Switchback — because the best part of the ride isn't always the destination.**
