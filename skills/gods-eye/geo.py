#!/usr/bin/env python3
"""gods-eye geo.py — keyless live geospatial queries.

Part of the `gods-eye` workspace skill. Concept inspired by
bilawalsidhu/gods-eye-view (MIT); all queries below hit keyless public APIs.

Usage:
    geo.py flights      --lat <LAT> --lon <LON> --radius-km 100
    geo.py iss-passes   --lat <LAT> --lon <LON> --days 3
    geo.py earthquakes  --lat <LAT> --lon <LON> --radius-km 300 --days 7 --min-mag 2.5
    geo.py weather      --lat <LAT> --lon <LON>
    geo.py fires        --lat <LAT> --lon <LON> --radius-km 400
    geo.py cyclones
    geo.py launches     --limit 5
    geo.py traffic-cam  --lat <LAT> --lon <LON> --radius-km 50
    geo.py sat-photo    --lat <LAT> --lon <LON> --days-back 7
    geo.py cables       --lat <LAT> --lon <LON> --radius-km 500
    geo.py radio        --lat <LAT> --lon <LON> --radius-km 100
    geo.py elevation    --lat <LAT> --lon <LON>
    geo.py installations --lat <LAT> --lon <LON> --radius-km 200
    geo.py eta          --lat <LAT> --lon <LON> --dest-lat <DEST_LAT> --dest-lon <DEST_LON>

Image commands (traffic-cam, sat-photo) save PNGs under the skill's cache/
directory and print the saved path. Every generated image gets a unique
timestamped filename.

All times print in the timezone named by GODS_EYE_TZ (default UTC). Exit 0 with a readable line even when a
query legitimately returns nothing; exit non-zero with a plain-English error
on failure (never fake data).
"""

import argparse
import datetime as dt
import os
import math
import sys
from zoneinfo import ZoneInfo

try:
    import requests
except ImportError:
    sys.stderr.write(
        "Error: the 'requests' package is missing. Run:\n"
        "  .venv/bin/pip install requests sgp4   (run inside this skill folder)\n"
    )
    sys.exit(2)

LOCAL_TZ = ZoneInfo(os.environ.get("GODS_EYE_TZ", "UTC"))
UTC = dt.timezone.utc
UA = {"User-Agent": "gods-eye-skill/1.0 (personal research tool; contact: none)"}
HTTP_TIMEOUT = 20

HOME_LAT = float(os.environ["GODS_EYE_HOME_LAT"]) if os.environ.get("GODS_EYE_HOME_LAT") else None
HOME_LON = float(os.environ["GODS_EYE_HOME_LON"]) if os.environ.get("GODS_EYE_HOME_LON") else None


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def fail(msg):
    sys.stderr.write(f"Error: {msg}\n")
    sys.exit(1)


def http_get(url, params=None):
    try:
        r = requests.get(url, params=params, headers=UA, timeout=HTTP_TIMEOUT)
    except requests.exceptions.Timeout:
        fail(f"request timed out: {url}")
    except requests.exceptions.ConnectionError:
        fail(f"could not reach {url} (network/DNS problem)")
    except requests.exceptions.RequestException as e:
        fail(f"request failed for {url}: {e}")
    if r.status_code != 200:
        fail(f"{url} returned HTTP {r.status_code}")
    try:
        return r.json()
    except ValueError:
        fail(f"{url} did not return JSON")


def haversine_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(a))


def compass(lat1, lon1, lat2, lon2):
    """Bearing from point 1 to point 2 as e.g. 'NE (42 deg)'."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    brg = (math.degrees(math.atan2(x, y)) + 360) % 360
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return f"{dirs[int((brg + 22.5) // 45) % 8]} ({brg:.0f} deg)"


def denver_time(moment_utc):
    return moment_utc.astimezone(LOCAL_TZ).strftime("%a %b %d, %-I:%M %p %Z")


# --------------------------------------------------------------------------
# flights — adsb.lol (data: ODbL, adsb.lol contributors)
# --------------------------------------------------------------------------
def cmd_flights(args):
    url = (
        f"https://api.adsb.lol/v2/lat/{args.lat}/lon/{args.lon}/dist/{args.radius_km}"
    )
    data = http_get(url)
    ac = data.get("ac") or []
    if not ac:
        print(
            f"No aircraft reporting within {args.radius_km} km of "
            f"{args.lat:.2f}, {args.lon:.2f} right now."
        )
        return

    rows = []
    for a in ac:
        alat, alon = a.get("lat"), a.get("lon")
        if alat is None or alon is None:
            continue
        dist = haversine_km(args.lat, args.lon, alat, alon)
        callsign = (a.get("flight") or "").strip() or f"hex/{a.get('hex', '?')}"
        ident = callsign
        extra = []
        if a.get("t"):
            extra.append(a["t"])
        if a.get("r"):
            extra.append(a["r"])
        if extra:
            ident += f" ({', '.join(extra)})"
        alt = a.get("alt_baro") or a.get("alt_geom")
        alt_s = f"{alt:,} ft" if isinstance(alt, (int, float)) else "alt n/a"
        gs = a.get("gs")
        gs_s = f"{gs:.0f} kt" if isinstance(gs, (int, float)) else "speed n/a"
        rows.append((dist, f"{ident} — {alt_s}, {gs_s}, {dist:.0f} km {compass(args.lat, args.lon, alat, alon)}"))

    rows.sort(key=lambda r: r[0])
    print(f"{len(rows)} aircraft within {args.radius_km} km of {args.lat:.2f}, {args.lon:.2f}:")
    for _, line in rows[:15]:
        print(line)
    if len(rows) > 15:
        print(f"...and {len(rows) - 15} more")


# --------------------------------------------------------------------------
# iss-passes — CelesTrak TLE + sgp4 propagation
# --------------------------------------------------------------------------
def _gmst_rad(jd_full):
    t = (jd_full - 2451545.0) / 36525.0
    g = 280.46061837 + 360.98564736629 * (jd_full - 2451545.0) + 0.000387933 * t * t - t**3 / 38710000.0
    return math.radians(g % 360.0)


def _observer_ecef(lat_deg, lon_deg):
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    a = 6378.137
    e2 = 1 - (1 - 1 / 298.257223563) ** 2
    n = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)
    return (
        n * math.cos(lat) * math.cos(lon),
        n * math.cos(lat) * math.sin(lon),
        n * (1 - e2) * math.sin(lat),
    )


def _elevation_deg(sat, moment_utc, obs_ecef, lat_deg, lon_deg):
    from sgp4.api import jday

    jd, fr = jday(
        moment_utc.year, moment_utc.month, moment_utc.day,
        moment_utc.hour, moment_utc.minute,
        moment_utc.second + moment_utc.microsecond / 1e6,
    )
    err, r_eci, _v = sat.sgp4(jd, fr)
    if err != 0:
        raise RuntimeError(f"SGP4 propagation error code {err}")
    g = _gmst_rad(jd + fr)
    cg, sg = math.cos(g), math.sin(g)
    # TEME -> ECEF (rotate by GMST about z)
    rx = cg * r_eci[0] + sg * r_eci[1]
    ry = -sg * r_eci[0] + cg * r_eci[1]
    rz = r_eci[2]
    dx, dy, dz = rx - obs_ecef[0], ry - obs_ecef[1], rz - obs_ecef[2]
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    slat, clat, slon, clon = math.sin(lat), math.cos(lat), math.sin(lon), math.cos(lon)
    east = -slon * dx + clon * dy
    north = -slat * clon * dx - slat * slon * dy + clat * dz
    up = clat * clon * dx + clat * slon * dy + slat * dz
    rng = math.sqrt(dx * dx + dy * dy + dz * dz)
    return math.degrees(math.asin(max(-1.0, min(1.0, up / rng))))


def cmd_iss(args):
    try:
        from sgp4.api import Satrec
    except ImportError:
        fail("the 'sgp4' package is missing. Run: ~/workspace/custom-skills/local-gods-eye/.venv/bin/pip install sgp4")

    # CelesTrak returns plain text, not JSON — fetch raw
    try:
        r = requests.get(
            "https://celestrak.org/NORAD/elements/gp.php",
            params={"CATNR": 25544, "FORMAT": "TLE"},
            headers=UA, timeout=HTTP_TIMEOUT,
        )
    except requests.exceptions.RequestException as e:
        fail(f"could not fetch ISS TLE from CelesTrak: {e}")
    if r.status_code != 200:
        fail(f"CelesTrak returned HTTP {r.status_code}")
    lines = [ln.strip() for ln in r.text.strip().splitlines() if ln.strip()]
    if len(lines) < 2 or not lines[-2].startswith("1 ") or not lines[-1].startswith("2 "):
        fail("CelesTrak did not return a valid two-line element set")
    sat = Satrec.twoline2rv(lines[-2], lines[-1])

    now = dt.datetime.now(UTC).replace(microsecond=0)
    end = now + dt.timedelta(days=args.days)
    step = dt.timedelta(seconds=30)
    obs = _observer_ecef(args.lat, args.lon)

    # coarse scan for above-horizon intervals
    samples = []
    t = now
    while t <= end:
        samples.append((t, _elevation_deg(sat, t, obs, args.lat, args.lon)))
        t += step

    passes = []
    i = 0
    n = len(samples)
    while i < n:
        if samples[i][1] > 0:
            j = i
            while j < n and samples[j][1] > 0:
                j += 1
            # refine rise/set by bisection on the 0-deg crossing
            def bisect(ta, ea, tb, eb):
                for _ in range(24):
                    tm = ta + (tb - ta) / 2
                    em = _elevation_deg(sat, tm, obs, args.lat, args.lon)
                    if (ea < 0) == (em < 0):
                        ta, ea = tm, em
                    else:
                        tb, eb = tm, em
                return tm

            t_rise = bisect(samples[i - 1][0], samples[i - 1][1], samples[i][0], samples[i][1]) if i > 0 else samples[i][0]
            t_set = bisect(samples[j - 1][0], samples[j - 1][1], samples[j][0], samples[j][1]) if j < n else samples[j - 1][0]
            # fine scan for max elevation
            best_t, best_el = t_rise, 0.0
            tc = t_rise
            while tc <= t_set:
                e = _elevation_deg(sat, tc, obs, args.lat, args.lon)
                if e > best_el:
                    best_el, best_t = e, tc
                tc += dt.timedelta(seconds=10)
            if best_el > 10:
                passes.append((t_rise, best_t, t_set, best_el))
            i = j
        else:
            i += 1

    if not passes:
        print(f"No ISS passes above 10 deg elevation in the next {args.days} days for {args.lat:.2f}, {args.lon:.2f}.")
        return
    print(f"ISS passes (max elevation > 10 deg) for {args.lat:.2f}, {args.lon:.2f}, next {args.days} days:")
    for rise, peak, set_, maxel in passes:
        print(
            f"Rise {denver_time(rise)} — peak {denver_time(peak)} at {maxel:.0f} deg — set {denver_time(set_)}"
        )


# --------------------------------------------------------------------------
# earthquakes — USGS FDSN (public domain)
# --------------------------------------------------------------------------
def cmd_quakes(args):
    start = (dt.datetime.now(UTC) - dt.timedelta(days=args.days)).strftime("%Y-%m-%d")
    data = http_get(
        "https://earthquake.usgs.gov/fdsnws/event/1/query",
        params={
            "format": "geojson",
            "latitude": args.lat,
            "longitude": args.lon,
            "maxradiuskm": args.radius_km,  # FDSN: kilometers
            "starttime": start,
            "minmagnitude": args.min_mag,
            "orderby": "time",
        },
    )
    feats = data.get("features") or []
    if not feats:
        print(
            f"No earthquakes M{args.min_mag}+ within {args.radius_km} km of "
            f"{args.lat:.2f}, {args.lon:.2f} in the last {args.days} days."
        )
        return
    print(f"{len(feats)} earthquakes M{args.min_mag}+ within {args.radius_km} km, last {args.days} days (newest first):")
    for f in feats[:20]:
        p = f.get("properties", {})
        mag = p.get("mag")
        place = p.get("place", "unknown location")
        t = p.get("time")
        when = denver_time(dt.datetime.fromtimestamp(t / 1000, UTC)) if t else "time n/a"
        coords = (f.get("geometry") or {}).get("coordinates") or []
        depth = f"{coords[2]:.1f} km deep" if len(coords) > 2 and coords[2] is not None else "depth n/a"
        print(f"M{mag:.1f} — {place} — {when} — {depth}" if isinstance(mag, (int, float)) else f"M? — {place} — {when} — {depth}")
    if len(feats) > 20:
        print(f"...and {len(feats) - 20} more")


# --------------------------------------------------------------------------
# weather — Open-Meteo (CC-BY 4.0)
# --------------------------------------------------------------------------
WMO = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "foggy", 48: "foggy with rime", 51: "light drizzle", 53: "drizzle",
    55: "heavy drizzle", 56: "freezing drizzle", 57: "freezing drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain", 66: "freezing rain",
    67: "freezing rain", 71: "light snow", 73: "snow", 75: "heavy snow",
    77: "snow grains", 80: "light showers", 81: "showers", 82: "heavy showers",
    85: "light snow showers", 86: "snow showers", 95: "thunderstorm",
    96: "thunderstorm with hail", 99: "thunderstorm with hail",
}


def cmd_weather(args):
    data = http_get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": args.lat,
            "longitude": args.lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "timezone": os.environ.get("GODS_EYE_TZ", "UTC"),
        },
    )
    c = data.get("current") or {}
    if "temperature_2m" not in c:
        fail("Open-Meteo did not return current conditions")
    desc = WMO.get(c.get("weather_code"), "unknown conditions")
    print(
        f"Now near {args.lat:.2f}, {args.lon:.2f}: {c['temperature_2m']:.0f}F "
        f"(feels {c.get('apparent_temperature', float('nan')):.0f}F), {desc}, "
        f"humidity {c.get('relative_humidity_2m', '?')}%, wind {c.get('wind_speed_10m', '?')} mph."
    )


# --------------------------------------------------------------------------
# fires — NIFC WFIGS current perimeters (ArcGIS REST, public domain)
# --------------------------------------------------------------------------
def cmd_fires(args):
    # Endpoint and field list copied from the gods-eye-view repo's own server
    # provider (server/providers/firePerimeters.js), which proxies this same
    # public keyless service.
    base = (
        "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/"
        "WFIGS_Interagency_Perimeters_Current/FeatureServer/0/query"
    )
    dlat = args.radius_km / 111.0
    dlon = args.radius_km / (111.0 * max(0.2, math.cos(math.radians(args.lat))))
    envelope = f"{args.lon - dlon},{args.lat - dlat},{args.lon + dlon},{args.lat + dlat}"
    data = http_get(base, params={
        "where": "1=1",
        "geometry": envelope,
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": ",".join([
            "poly_IncidentName", "attr_IncidentSize", "attr_PercentContained",
            "attr_POOState", "attr_POOCounty", "attr_FireDiscoveryDateTime",
            "poly_DateCurrent", "attr_IncidentTypeCategory",
        ]),
        "maxAllowableOffset": "0.01",
        "outSR": "4326",
        "returnGeometry": "true",
        "f": "geojson",
    })
    feats = data.get("features") or []
    if not feats:
        print(f"No current wildfire perimeters within {args.radius_km} km of {args.lat:.2f}, {args.lon:.2f}.")
        return

    def centroid(geom):
        # bbox center of first polygon ring — good enough for distance text
        coords = []
        gtype = geom.get("type")
        polys = geom.get("coordinates") or []
        if gtype == "Polygon":
            rings = polys
        elif gtype == "MultiPolygon":
            rings = [r for poly in polys for r in poly]
        else:
            return None
        for ring in rings:
            coords.extend(ring)
        if not coords:
            return None
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        return ((min(lats) + max(lats)) / 2, (min(lons) + max(lons)) / 2)

    rows = []
    for f in feats:
        p = f.get("properties", {}) or {}
        c = centroid(f.get("geometry") or {})
        if c is None:
            continue
        dist = haversine_km(args.lat, args.lon, c[0], c[1])
        name = p.get("poly_IncidentName") or "Unnamed fire"
        size = p.get("attr_IncidentSize")
        size_s = f"{size:,.0f} acres" if isinstance(size, (int, float)) else "size n/a"
        cont = p.get("attr_PercentContained")
        cont_s = f"{cont:.0f}% contained" if isinstance(cont, (int, float)) else "containment n/a"
        where = ", ".join(x for x in [p.get("attr_POOCounty"), p.get("attr_POOState")] if x) or "location n/a"
        disc = p.get("attr_FireDiscoveryDateTime")
        if disc:
            try:
                disc_s = "discovered " + dt.datetime.fromtimestamp(disc / 1000, UTC).astimezone(LOCAL_TZ).strftime("%b %d, %-I:%M %p")
            except Exception:
                disc_s = ""
        else:
            disc_s = ""
        if dist > args.radius_km:
            continue
        rows.append((dist, f"{name} — {size_s}, {cont_s} — {where} — {dist:.0f} km {compass(args.lat, args.lon, c[0], c[1])}" + (f" — {disc_s}" if disc_s else "")))

    rows.sort(key=lambda r: r[0])
    print(f"{len(rows)} current wildfire perimeters within {args.radius_km} km of {args.lat:.2f}, {args.lon:.2f} (nearest first):")
    for _, line in rows[:15]:
        print(line)
    if len(rows) > 15:
        print(f"...and {len(rows) - 15} more")


# --------------------------------------------------------------------------
# cyclones — NHC CurrentStorms.json
# --------------------------------------------------------------------------
BASINS = {"at": "Atlantic", "ep": "East Pacific", "cp": "Central Pacific",
          "wp": "West Pacific", "io": "Indian Ocean", "sh": "Southern Hemisphere"}


def cmd_cyclones(_args):
    data = http_get("https://www.nhc.noaa.gov/CurrentStorms.json")
    storms = data.get("activeStorms") or []
    if not storms:
        print("No active tropical cyclones worldwide right now.")
        return
    print(f"{len(storms)} active tropical cyclones:")
    for s in storms:
        name = s.get("name") or "Unnamed"
        binno = (s.get("binNumber") or "")[:2].lower()
        basin = BASINS.get(binno) or BASINS.get((s.get("id") or "")[:2].lower(), "?")
        cls = s.get("classification") or ""
        inten = s.get("intensity")
        inten_s = f"{inten} kt" if inten else "intensity n/a"
        loc = ""
        la, lo = s.get("latitude"), s.get("longitude")
        if la and lo:
            loc = f" — {la} {lo}"
        print(f"{name} ({basin}) — {cls} {inten_s}{loc}".strip())


# --------------------------------------------------------------------------
# launches — The Space Devs Launch Library 2 (keyless, 15 calls/hr)
# --------------------------------------------------------------------------
def cmd_launches(args):
    data = http_get(
        "https://ll.thespacedevs.com/2.3.0/launches/upcoming/",
        params={"limit": args.limit},
    )
    results = data.get("results") or []
    if not results:
        print("No upcoming launches listed.")
        return
    print(f"Next {len(results)} upcoming rocket launches:")
    for l in results:
        name = l.get("name") or "Unnamed launch"
        pad = (l.get("pad") or {}).get("name") or "pad n/a"
        loc = (l.get("pad") or {}).get("location", {}).get("name") or ""
        net = l.get("net")
        if net:
            try:
                when = denver_time(dt.datetime.fromisoformat(net.replace("Z", "+00:00")))
            except ValueError:
                when = net
        else:
            when = "time TBD"
        status = (l.get("status") or {}).get("abbrev") or ""
        where = f"{pad}, {loc}" if loc else pad
        line = f"{name} — {where} — {when}"
        if status:
            line += f" [{status}]"
        print(line)


# --------------------------------------------------------------------------
# traffic-cam — UDOT public traffic cameras (keyless website endpoints)
# --------------------------------------------------------------------------
UDOT_LIST = "https://www.udottraffic.utah.gov/List/GetData/Cameras"
UDOT_SNAP = "https://www.udottraffic.utah.gov/map/Cctv/{}"
CAM_CACHE_TTL = 24 * 3600
# sha256 of the known "This camera is offline" placeholder PNG
OFFLINE_PLACEHOLDER_SHA256 = "b9b4dc336246421065a66accf27768af3269a75e48cbacf0624aa2b0e9f59ef9"


def _cache_dir():
    import pathlib

    d = pathlib.Path(__file__).resolve().parent / "cache"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _load_udot_cameras(cache_dir):
    import json
    import time

    cache_file = cache_dir / "udot_cameras.json"
    if cache_file.exists() and time.time() - cache_file.stat().st_mtime < CAM_CACHE_TTL:
        try:
            return json.loads(cache_file.read_text())
        except (ValueError, OSError):
            pass
    cams = []
    start = 0
    while True:
        try:
            r = requests.post(
                UDOT_LIST,
                data={"draw": 1, "start": start, "length": 100},
                headers=UA,
                timeout=HTTP_TIMEOUT,
            )
        except requests.exceptions.RequestException as e:
            fail(f"could not reach UDOT camera list: {e}")
        if r.status_code != 200:
            fail(f"UDOT camera list returned HTTP {r.status_code}")
        try:
            page = r.json()
        except ValueError:
            fail("UDOT camera list did not return JSON")
        rows = page.get("data") or []
        for row in rows:
            wkt = ((row.get("latLng") or {}).get("geography") or {}).get("wellKnownText") or ""
            lat = lon = None
            if wkt.startswith("POINT"):
                try:
                    lon_s, lat_s = wkt[7:-1].split()
                    lat, lon = float(lat_s), float(lon_s)
                except ValueError:
                    pass
            if lat is None:
                continue
            cams.append({
                "id": str(row.get("id")),
                "location": row.get("location") or "unnamed camera",
                "roadway": row.get("roadway") or "",
                "direction": row.get("direction") or "",
                "lat": lat,
                "lon": lon,
            })
        if len(rows) < 100:
            break
        start += 100
    if not cams:
        fail("UDOT returned no cameras")
    try:
        cache_file.write_text(json.dumps(cams))
    except OSError:
        pass
    return cams


def _http_bytes(url):
    import hashlib

    try:
        r = requests.get(url, headers=UA, timeout=HTTP_TIMEOUT)
    except requests.exceptions.RequestException as e:
        return None, f"request failed: {e}"
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}"
    ctype = (r.headers.get("content-type") or "").split(";")[0].strip().lower()
    if not ctype.startswith("image/"):
        return None, f"not an image ({ctype or 'unknown type'})"
    digest = hashlib.sha256(r.content).hexdigest()
    if digest == OFFLINE_PLACEHOLDER_SHA256:
        return None, "camera offline (placeholder image)"
    return (r.content, ctype), None


def cmd_traffic_cam(args):
    cache_dir = _cache_dir()
    cams = _load_udot_cameras(cache_dir)
    rows = []
    for c in cams:
        d = haversine_km(args.lat, args.lon, c["lat"], c["lon"])
        if d <= args.radius_km:
            rows.append((d, c))
    rows.sort(key=lambda r: r[0])
    if not rows:
        print(f"No UDOT traffic cameras within {args.radius_km} km of {args.lat:.2f}, {args.lon:.2f}.")
        print("UDOT covers Utah highways; outside Utah there is no coverage from this source.")
        return
    print(f"{len(rows)} UDOT traffic cameras within {args.radius_km} km (nearest first):")
    for d, c in rows[:12]:
        bits = [c["location"]]
        if c["roadway"] and c["roadway"] != "Unknown":
            bits.append(c["roadway"])
        if c["direction"] and c["direction"] != "Unknown":
            bits.append(c["direction"])
        bits.append(f"{d:.1f} km {compass(args.lat, args.lon, c['lat'], c['lon'])}")
        print(" — ".join(bits))
    if len(rows) > 12:
        print(f"...and {len(rows) - 12} more")
    # snapshot from the nearest live camera (skip offline placeholders)
    stamp = dt.datetime.now(LOCAL_TZ).strftime("%Y%m%d_%H%M%S")
    for d, c in rows[:6]:
        (img, err) = _http_bytes(UDOT_SNAP.format(c["id"]))
        if img is None:
            continue
        content, ctype = img
        ext = ".jpg" if "jpeg" in ctype else ".png"
        path = cache_dir / f"traffic_cam_{c['id']}_{stamp}{ext}"
        try:
            path.write_bytes(content)
        except OSError as e:
            fail(f"could not save snapshot: {e}")
        print(f"Snapshot ({c['location']}, {d:.1f} km away) saved: {path}")
        return
    print("Nearest cameras appear offline right now; no live snapshot available.")


# --------------------------------------------------------------------------
# sat-photo — NASA Worldview Snapshots (GIBS, keyless, U.S. public domain)
# --------------------------------------------------------------------------
def cmd_satphoto(args):
    cache_dir = _cache_dir()
    half = 0.15  # ~30 km box
    box = (args.lat - half, args.lon - half, args.lat + half, args.lon + half)
    bbox = f"{box[0]:.6f},{box[1]:.6f},{box[2]:.6f},{box[3]:.6f}"
    today = dt.datetime.now(UTC).date()
    for back in range(1, args.days_back + 1):
        day = (today - dt.timedelta(days=back)).isoformat()
        url = (
            "https://wvs.earthdata.nasa.gov/api/v1/snapshot?REQUEST=GetSnapshot"
            "&LAYERS=VIIRS_NOAA21_CorrectedReflectance_TrueColor&CRS=EPSG:4326"
            f"&TIME={day}&BBOX={bbox}&WIDTH=1024&HEIGHT=1024&FORMAT=image/png"
        )
        try:
            r = requests.get(url, headers=UA, timeout=60)
        except requests.exceptions.RequestException:
            continue
        if r.status_code != 200:
            continue
        ctype = (r.headers.get("content-type") or "").split(";")[0].strip().lower()
        if not ctype.startswith("image/") or len(r.content) < 30000:
            continue
        stamp = dt.datetime.now(LOCAL_TZ).strftime("%Y%m%d_%H%M%S")
        path = cache_dir / f"satphoto_{day}_{stamp}.png"
        try:
            path.write_bytes(r.content)
        except OSError as e:
            fail(f"could not save satellite image: {e}")
        print(f"True-color satellite image ({day}, VIIRS 250 m) of {args.lat:.2f}, {args.lon:.2f} saved: {path}")
        return
    fail(f"no usable satellite image for the last {args.days_back} days (service may be down)")


# --------------------------------------------------------------------------
# cables — bundled TeleGeography submarine cable paths (local file)
# --------------------------------------------------------------------------
def _point_seg_dist_km(plat, plon, alat, alon, blat, blon):
    # equirectangular projection around the point; good for short distances
    kx = 111.320 * math.cos(math.radians(plat))
    ky = 110.574
    px, py = (plon - 0) * kx, (plat - 0) * ky
    ax, ay = (alon - 0) * kx, (alat - 0) * ky
    bx, by = (blon - 0) * kx, (blat - 0) * ky
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def cmd_cables(args):
    import json
    import pathlib

    src = pathlib.Path(__file__).resolve().parent / "data" / "cable-geo.json"
    try:
        fc = json.loads(src.read_text())
    except (OSError, ValueError) as e:
        fail(f"could not read bundled cable data: {e}")
    rows = []
    for feat in fc.get("features") or []:
        props = feat.get("properties") or {}
        name = props.get("name") or "Unnamed cable"
        geom = feat.get("geometry") or {}
        if geom.get("type") != "MultiLineString":
            continue
        best = None
        for line in geom.get("coordinates") or []:
            for i in range(len(line) - 1):
                (alon, alat), (blon, blat) = line[i], line[i + 1]
                d = _point_seg_dist_km(args.lat, args.lon, alat, alon, blat, blon)
                if best is None or d < best:
                    best = d
        if best is not None and best <= args.radius_km:
            rows.append((best, name))
    # de-duplicate by cable name, keep nearest
    seen = {}
    for d, name in rows:
        if name not in seen or d < seen[name]:
            seen[name] = d
    rows = sorted(seen.items(), key=lambda kv: kv[1])
    if not rows:
        print(f"No submarine cables within {args.radius_km} km of {args.lat:.2f}, {args.lon:.2f}.")
        print("(Cables are undersea; inland locations like Utah will usually show none.)")
        return
    print(f"{len(rows)} submarine cables within {args.radius_km} km (nearest first):")
    for name, d in rows[:15]:
        print(f"{name} — nearest point {d:.0f} km away")
    if len(rows) > 15:
        print(f"...and {len(rows) - 15} more")


# --------------------------------------------------------------------------
# radio — Radio Browser directory (keyless) via Nominatim reverse-geocode
# --------------------------------------------------------------------------
RADIO_MIRRORS = [
    "https://de1.api.radio-browser.info",
    "https://nl1.api.radio-browser.info",
    "https://de2.api.radio-browser.info",
]


def cmd_radio(args):
    rev = http_get(
        "https://nominatim.openstreetmap.org/reverse",
        params={"lat": args.lat, "lon": args.lon, "format": "json"},
    )
    addr = rev.get("address") or {}
    state = addr.get("state")
    cc = (addr.get("country_code") or "").upper()
    stations = None
    last_err = "no mirror answered"
    for host in RADIO_MIRRORS:
        params = {"hidebroken": "true", "order": "votes", "reverse": "true", "limit": 100}
        if state:
            params["state"] = state
        if cc:
            params["countrycode"] = cc
        try:
            r = requests.get(f"{host}/json/stations/search", params=params, headers=UA, timeout=HTTP_TIMEOUT)
        except requests.exceptions.RequestException as e:
            last_err = str(e)
            continue
        if r.status_code != 200:
            last_err = f"HTTP {r.status_code}"
            continue
        try:
            stations = r.json()
        except ValueError:
            last_err = "bad JSON"
            continue
        break
    if stations is None:
        fail(f"Radio Browser directory is unreachable ({last_err})")
    rows = []
    ungeocoded = 0
    for s in stations:
        name = s.get("name") or "Unnamed station"
        glat, glon = s.get("geo_lat"), s.get("geo_long")
        dist = None
        if isinstance(glat, (int, float)) and isinstance(glon, (int, float)):
            dist = haversine_km(args.lat, args.lon, glat, glon)
            if dist > args.radius_km:
                continue
        else:
            ungeocoded += 1
            if args.strict_geo:
                continue
        tags = ", ".join((s.get("tags") or "").split(",")[:3])
        br = s.get("bitrate")
        br_s = f"{br} kbps" if br else "bitrate n/a"
        url = s.get("url_resolved") or s.get("url") or ""
        line = f"{name} — {br_s}"
        if tags:
            line += f" — {tags}"
        if dist is not None:
            line += f" — {dist:.0f} km away"
        if url:
            line += f"\n    stream: {url}"
        rows.append(((dist if dist is not None else 1e9), line))
    rows.sort(key=lambda r: r[0])
    if not rows:
        print(f"No radio stations found near {args.lat:.2f}, {args.lon:.2f}.")
        return
    print(f"{len(rows)} internet radio stations (best first):")
    for _, line in rows[:12]:
        print(line)
    if len(rows) > 12:
        print(f"...and {len(rows) - 12} more")
    if ungeocoded:
        print(f"(note: {ungeocoded} stations publish no location)")


# --------------------------------------------------------------------------
# elevation — OpenTopoData (keyless, 1000 calls/day)
# --------------------------------------------------------------------------
def cmd_elevation(args):
    data = http_get(
        "https://api.opentopodata.org/v1/mapzen",
        params={"locations": f"{args.lat},{args.lon}"},
    )
    results = data.get("results") or []
    if not results or results[0].get("elevation") is None:
        fail("OpenTopoData returned no elevation for that point")
    m = results[0]["elevation"]
    print(f"Elevation at {args.lat:.4f}, {args.lon:.4f}: {m:,.0f} m ({m * 3.28084:,.0f} ft).")


# --------------------------------------------------------------------------
# installations — bundled OSM/Overture military installation names (local)
# --------------------------------------------------------------------------
def cmd_installations(args):
    import json
    import pathlib

    src = pathlib.Path(__file__).resolve().parent / "data" / "names.json"
    try:
        pack = json.loads(src.read_text())
    except (OSError, ValueError) as e:
        fail(f"could not read bundled installation data: {e}")
    classes = pack.get("classes") or []
    rows = []
    for rec in pack.get("records") or []:
        try:
            _key, name, clon, clat, _w, _s, _e, _n, kind, _area = rec
        except (ValueError, TypeError):
            continue
        if not isinstance(clat, (int, float)) or not isinstance(clon, (int, float)):
            continue
        d = haversine_km(args.lat, args.lon, clat, clon)
        if d <= args.radius_km:
            cls = classes[kind] if isinstance(kind, int) and 0 <= kind < len(classes) else "site"
            rows.append((d, f"{name or 'Unnamed site'} — {cls.replace('_', ' ')} — {d:.0f} km {compass(args.lat, args.lon, clat, clon)}"))
    rows.sort(key=lambda r: r[0])
    if not rows:
        print(f"No recorded military installations within {args.radius_km} km of {args.lat:.2f}, {args.lon:.2f}.")
        return
    print(f"{len(rows)} military installations/sites within {args.radius_km} km (nearest first):")
    for _, line in rows[:15]:
        print(line)
    if len(rows) > 15:
        print(f"...and {len(rows) - 15} more")


# --------------------------------------------------------------------------
# eta — live drive time and distance (OSRM demo server, keyless)
# --------------------------------------------------------------------------
def cmd_eta(args):
    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{args.lon},{args.lat};{args.dest_lon},{args.dest_lat}"
    )
    try:
        r = requests.get(url, params={"overview": "false"}, headers=UA, timeout=HTTP_TIMEOUT)
    except requests.exceptions.Timeout:
        fail("OSRM routing request timed out")
    except requests.exceptions.ConnectionError:
        fail("could not reach the OSRM routing server (network/DNS problem)")
    except requests.exceptions.RequestException as e:
        fail(f"OSRM routing request failed: {e}")
    if r.status_code == 400:
        fail("OSRM rejected the request (check the coordinates)")
    if r.status_code == 429:
        fail("OSRM rate-limited the request; wait a minute and try again")
    if r.status_code >= 400:
        fail(f"OSRM routing failed (HTTP {r.status_code})")
    try:
        data = r.json()
    except ValueError:
        fail("OSRM did not return JSON")
    if data.get("code") != "Ok" or not data.get("routes"):
        msg = data.get("message") or "no route found"
        fail(f"OSRM could not route that trip ({msg})")
    route = data["routes"][0]
    secs = route.get("duration")
    meters = route.get("distance")
    if secs is None or meters is None:
        fail("OSRM returned a route without time/distance")
    mins = int(round(secs / 60))
    if mins >= 60:
        h, m = divmod(mins, 60)
        timestr = f"{h} hr {m} min" if m else f"{h} hr"
    else:
        timestr = f"{mins} min"
    print(f"Drive time: {timestr} ({meters / 1000:.1f} km) via current roads")


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(prog="geo.py", description="Keyless live geospatial queries (gods-eye skill).")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--lat", type=float, default=HOME_LAT, help="latitude (default: GODS_EYE_HOME_LAT)")
    common.add_argument("--lon", type=float, default=HOME_LON, help=f"longitude (default {HOME_LON})")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("flights", parents=[common], help="live aircraft overhead (adsb.lol)")
    p.add_argument("--radius-km", type=float, default=100)

    p = sub.add_parser("iss-passes", parents=[common], help="upcoming ISS passes (CelesTrak TLE + SGP4)")
    p.add_argument("--days", type=int, default=3)

    p = sub.add_parser("earthquakes", parents=[common], help="recent earthquakes (USGS)")
    p.add_argument("--radius-km", type=float, default=300)
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--min-mag", type=float, default=2.5)

    sub.add_parser("weather", parents=[common], help="current weather (Open-Meteo)")

    p = sub.add_parser("fires", parents=[common], help="current wildfire perimeters (NIFC WFIGS)")
    p.add_argument("--radius-km", type=float, default=400)

    sub.add_parser("cyclones", parents=[common], help="active tropical cyclones (NHC)")

    p = sub.add_parser("launches", parents=[common], help="upcoming rocket launches (The Space Devs)")
    p.add_argument("--limit", type=int, default=5)

    p = sub.add_parser("traffic-cam", parents=[common], help="UDOT traffic cameras nearby + live snapshot")
    p.add_argument("--radius-km", type=float, default=50)

    p = sub.add_parser("sat-photo", parents=[common], help="recent true-color satellite image (NASA)")
    p.add_argument("--days-back", type=int, default=7)

    p = sub.add_parser("cables", parents=[common], help="submarine cables near a point (bundled data)")
    p.add_argument("--radius-km", type=float, default=500)

    p = sub.add_parser("radio", parents=[common], help="internet radio stations near a point (Radio Browser)")
    p.add_argument("--radius-km", type=float, default=100)
    p.add_argument("--strict-geo", action="store_true",
                   help="only stations publishing coordinates within the radius")

    sub.add_parser("elevation", parents=[common], help="elevation in m/ft (OpenTopoData)")

    p = sub.add_parser("installations", parents=[common], help="military installations nearby (bundled OSM/Overture data)")
    p.add_argument("--radius-km", type=float, default=200)

    p = sub.add_parser("eta", parents=[common], help="drive time and distance between two points (OSRM)")
    p.add_argument("--dest-lat", type=float, required=True, help="destination latitude")
    p.add_argument("--dest-lon", type=float, required=True, help="destination longitude")

    args = ap.parse_args()
    if hasattr(args, "lat") and (args.lat is None or args.lon is None):
        fail("This command needs a location: pass --lat and --lon, or set GODS_EYE_HOME_LAT and GODS_EYE_HOME_LON.")
    try:
        {
            "flights": cmd_flights,
            "iss-passes": cmd_iss,
            "earthquakes": cmd_quakes,
            "weather": cmd_weather,
            "fires": cmd_fires,
            "cyclones": cmd_cyclones,
            "launches": cmd_launches,
            "traffic-cam": cmd_traffic_cam,
            "sat-photo": cmd_satphoto,
            "cables": cmd_cables,
            "radio": cmd_radio,
            "elevation": cmd_elevation,
            "installations": cmd_installations,
            "eta": cmd_eta,
        }[args.cmd](args)
    except BrokenPipeError:
        sys.exit(0)
    except Exception as e:  # never fake data, never empty-success
        fail(f"unexpected failure: {e}")


if __name__ == "__main__":
    main()
