---
name: nasa-eonet
description: Live natural events worldwide (severe storms, wildfires, volcanoes, earthquakes, floods, landslides and more) from NASA's free EONET API v3. No API key or signup. Use for map event layers, "what is happening near this place" checks, tracking an active storm or fire over time, or alerting on new events in an area.
---

# nasa-eonet

NASA's Earth Observatory Natural Event Tracker (EONET) catalogs natural
events happening around the world, curated from sources like JTWC,
InciWeb, USGS and NASA Earth Observatory, and serves them from a free
JSON API. No key, no auth, no signup.

Base URL: `https://eonet.gsfc.nasa.gov/api/v3`
Docs: https://eonet.gsfc.nasa.gov/docs/v3

## Tool

`eonet.py` in this skill folder: a small Python CLI that uses only the
Python standard library (urllib + json), so there is no virtualenv to
maintain. Run it directly:

```
eonet.py categories
eonet.py events --category wildfires --days 7 --limit 10
eonet.py events --bbox=-125,50,-66,24 --days 3
eonet.py events --category severeStorms --raw
```

Each `events` line prints: title | categories | open or closed | the
latest geometry point as lat, lon with its date, plus magnitude when the
source provides one.

## Endpoints

| Endpoint | Returns |
| --- | --- |
| `GET /events` | Events as JSON (filters below) |
| `GET /events/geojson` | The same events as a GeoJSON FeatureCollection, ready for map libraries |
| `GET /events/{id}` | One event with its full geometry history |
| `GET /categories` | The 13 categories |
| `GET /categories/{categoryId}` | Events in one category |
| `GET /sources` | The curation sources (InciWeb, JTWC, EO, ...) usable as a filter |
| `GET /layers/{categoryId}` | NASA imagery web services (WMS/WMTS) mapped to a category |

## Filters (events and geojson)

| Param | Notes |
| --- | --- |
| `source` | Source ID, comma separated, boolean OR |
| `category` | Category ID, comma separated, boolean OR |
| `status` | `open` (default), `closed`, or `all` |
| `limit` | Max events returned |
| `days` | Only events from the last N days, including today |
| `start`, `end` | Date range, YYYY-MM-DD, inclusive |
| `magID`, `magMin`, `magMax` | Magnitude filter, e.g. `magID=mag_kts` for storm winds |
| `bbox` | `minLon,maxLat,maxLon,minLat`: the upper left corner, then the lower right |

Always pass `days` and `limit` explicitly. An unfiltered call returns
every open event worldwide and is a big payload.

## Categories

| ID | Title |
| --- | --- |
| `drought` | Drought |
| `dustHaze` | Dust and Haze |
| `earthquakes` | Earthquakes |
| `floods` | Floods |
| `landslides` | Landslides |
| `manmade` | Manmade |
| `seaLakeIce` | Sea and Lake Ice |
| `severeStorms` | Severe Storms |
| `snow` | Snow |
| `tempExtremes` | Temperature Extremes |
| `volcanoes` | Volcanoes |
| `waterColor` | Water Color |
| `wildfires` | Wildfires |

## Response shape

An event object carries: `id`, `title`, `description` (often null),
`link`, `closed` (null while the event is open, otherwise the date/time
it ended), `categories`, `sources` (id + url), and `geometry`.

Each geometry entry pairs a `date` with a GeoJSON `Point` or `Polygon`
and, when the source provides it, `magnitudeValue`, `magnitudeUnit` and
`magnitudeDescription`. The geometry series is the event's track over
time: a storm's path, a fire's growing perimeter.

## Gotchas

- **Coordinates are GeoJSON order: [longitude, latitude].** Most UI and
  map code wants lat, lon. Flip them, or every event lands in the ocean
  off the wrong continent.
- **Magnitude lives on each geometry entry, not on the event**, and the
  units vary by category (storm winds in kts, quakes in Richter
  magnitude, fire size in acres). Never compare magnitudes across
  categories.
- Geometry dates are 00:00Z unless the source reported a real time.
- `closed` is approximate for some event types, and events get
  re-curated. Treat EONET as near real time, not a sensor feed: poll
  minutes apart at most, and cache responses.
- `description` is often null. Title, category and sources carry the
  information.
- The API is free with no key. Be a good citizen and do not hammer it.

## What it is good for

- A natural events layer on a live map: use the geojson endpoint and
  poll every few minutes.
- "Any wildfires or storms near this place right now": a `bbox` around
  the place with small `days`.
- Following one event: fetch `/events/{id}` and read its geometry series
  in date order.
- Daily briefings: open events by category with `days=1`.

Data is NASA EONET and subject to NASA's EONET disclaimer. Keep the
per-event source links when displaying events.
