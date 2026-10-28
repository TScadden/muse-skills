---
name: gods-eye
description: Live geospatial answers from keyless public APIs: planes overhead, ISS passes, recent earthquakes, current weather, wildfires, tropical cyclones, rocket launches, traffic cameras (Utah), satellite photos, submarine cables, radio stations, elevation, and drive time.
---

# gods-eye

Live geospatial answers from keyless public APIs. Use this skill when the user asks
what's happening in the sky or on the ground around a location: planes overhead
right now, when the ISS will pass, recent earthquakes, current weather,
wildfires nearby, active tropical cyclones, upcoming rocket launches, live UDOT
traffic-camera snapshots, recent satellite photos, submarine cables, nearby
radio stations, ground elevation, or military installations nearby, or drive time
between two points.

## Tool

`geo.py` in this skill folder — a small Python CLI. Create the skill venv
once (see SETUP.md), then run commands with `.venv/bin/python geo.py ...`:

```
geo.py <command> [options]
```

If the venv is ever missing, recreate it with:
`python3 -m venv .venv && .venv/bin/pip install requests sgp4` (inside this skill folder)

## Commands

Location: pass `--lat <LAT> --lon <LON>`, or set `GODS_EYE_HOME_LAT` and
`GODS_EYE_HOME_LON` once and every command defaults to home. All times print
in the timezone named by `GODS_EYE_TZ` (set it to your IANA timezone, for
example `America/New_York`; default UTC). Output is concise human-readable text, one result per line,
ready to paste into chat.

- `flights --lat <LAT> --lon <LON> --radius-km 100`
  Live aircraft in radius (adsb.lol). Shows callsign, type/registration,
  altitude, speed, distance and bearing from the point. Says so plainly when
  the sky is empty.
- `iss-passes --lat <LAT> --lon <LON> --days 3`
  Upcoming ISS passes. Fetches the current TLE from CelesTrak and propagates
  it with SGP4. Reports rise/peak/set with max elevation; only passes peaking
  above 10 degrees. Times are approximate (within ~a minute), good for
  "when do I look up" questions.
- `earthquakes --lat <LAT> --lon <LON> --radius-km 300 --days 7 --min-mag 2.5`
  Recent quakes (USGS). Shows magnitude, place, Denver time, depth.
  `maxradiuskm` is kilometers in the USGS FDSN API.
- `weather --lat <LAT> --lon <LON>`
  Current conditions (Open-Meteo): temperature, feels-like, conditions,
  humidity, wind. One line.
- `fires --lat <LAT> --lon <LON> --radius-km 400`
  Current wildfire perimeters near the point (NIFC WFIGS ArcGIS feature
  service, same public endpoint the God's Eye View repo proxies). Shows name,
  acres, containment, county/state, distance/bearing, discovery date.
- `cyclones`
  Active tropical cyclones worldwide (NHC): name, basin, classification,
  intensity, position.
- `launches --limit 5`
  Upcoming rocket launches (The Space Devs Launch Library 2): name,
  launch pad and location, liftoff time in Denver time.
- `traffic-cam --lat <LAT> --lon <LON> --radius-km 50`
  UDOT public traffic cameras near the point (Utah only): lists nearby
  cameras with intersection name, roadway, direction, distance/bearing, then
  saves a live snapshot PNG from the nearest working camera into the skill's
  `cache/` dir and prints the path. Offline cameras are skipped automatically.
  The camera list is cached for 24 hours.
- `sat-photo --lat <LAT> --lon <LON> --days-back 7`
  Recent true-color satellite image (NASA Worldview, VIIRS 250 m): tries the
  last `--days-back` days until one returns a usable image, saves the PNG to
  `cache/` with a unique timestamped filename, prints the path.
- `cables --lat <LAT> --lon <LON> --radius-km 500`
  Submarine cables near the point, from the repo's bundled TeleGeography
  paths (local file, no network). Inland points like Utah normally show none.
- `radio --lat <LAT> --lon <LON> --radius-km 100`
  Internet radio stations near the point (Radio Browser directory, keyless):
  reverse-geocodes the point to a state, lists stations by popularity with
  stream URLs. Stations that publish coordinates are filtered by radius.
- `elevation --lat <LAT> --lon <LON>`
  Ground elevation in meters and feet (OpenTopoData). One line.
- `installations --lat <LAT> --lon <LON> --radius-km 200`
  Military installations and ranges nearby, from the repo's bundled
  OSM/Overture military-names data (local file, no network): name, site
  class, distance/bearing.
- `eta --lat <LAT> --lon <LON> --dest-lat <DEST_LAT> --dest-lon <DEST_LON>`
  Live drive time and distance between two points (OSRM demo server,
  keyless): one line with minutes and kilometers via current roads.

## Rules

- Keyless only: no API keys, no signup. Make single queries; never poll in a
  loop (respect rate limits, especially adsb.lol, the ArcGIS service,
  The Space Devs at 15 calls/hour, and the OSRM demo server's fair use).
- Live ships are NOT included: the repo's vessel feed (AISStream.io) requires
  an API key, and we don't sign up for keys.
- The CLI exits non-zero with a plain-English error on failure. Never invent
  data. If a source is down or returns garbage, report that instead of
  guessing. An empty-but-valid result (no planes, no quakes) prints a clear
  "none found" line and exits 0.
- `flights` positions come from crowdsourced ADS-B feeders; coverage gaps
  mean "no aircraft shown" is not proof the sky is empty.
- Image outputs (`traffic-cam`, `sat-photo`) always use unique timestamped
  filenames — never reuse a filename (a standing rule in the original setup).

## Attribution

- Data: adsb.lol (ODbL, ADS-B Exchange contributors), USGS (U.S. public
  domain), CelesTrak (TLEs), Open-Meteo (CC-BY 4.0), NIFC WFIGS (U.S. public
  domain), National Hurricane Center (U.S. public domain), The Space Devs
  Launch Library 2, UDOT public traffic cameras, NASA Worldview/GIBS (U.S.
  public domain), TeleGeography submarine cable paths (bundled, non-commercial
  use), Radio Browser (community directory), OpenTopoData (various open
  DEM sources), OpenStreetMap + Overture Maps (ODbL) for installation names,
  OSRM demo server routing on OpenStreetMap data (ODbL).
- Code concept inspired by bilawalsidhu/gods-eye-view (MIT-licensed); this
  skill reimplements the key queries as a standalone keyless CLI and does not
  run that repo's stack.
## Available connectors

Use `muse.connector_search` to find the current connector docs before following
recovered instructions.
