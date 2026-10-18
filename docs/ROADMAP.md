# Switchback roadmap

Shipped: road discovery from OSM geometry, ranking, map UI, ride building with GraphHopper connectors, GPX export, hand-added roads, units, saved home, accounts (first-run admin, invites, password resets, roles).

## Next
- **Docker packaging** and a region-generic builder (`REGION=...`), so anyone can run it for their own area.
- **Desktop installers (Windows / Mac)** that wrap the same builder: download, double-click, pick your state(s). Needs code signing.
- **Phone app:** installable web app (PWA) with a phone layout, then maybe a native Android app.
- **Ride feedback:** a 10 to 15 second "was the ride fun?" flow with 3 to 5 follow-up questions.
- **Distance cap** for "Find next road" and clearer legs on long connectors.

## Ratings (requested)
Riders rate road segments, optionally with the date they rode them, and a matching filter and search finds highly rated segments.
- A rating is 1 to 5 stars, an optional ride date and an optional note, one per rider per road (editable, with history of dates ridden).
- Cards show the average, the number of ratings and "last ridden"; filters: rated at least N stars, rated by me, not yet ridden by me, ridden within a period; sort by rating.
- Needs **stable road ids first.** Scan candidates are currently numbered by position, so a rescan renumbers them and would orphan ratings. Key each road by something durable (for example a hash of its first and last OSM node ids plus its name) and migrate hand-added roads and saved rides to it.
- Storage: a `ratings` table in the SQLite store next to users and roads.

## Accounts, version 2
- OIDC / SSO login (for example Authentik), TOTP two-factor, exporting and importing hand-added roads between servers.
