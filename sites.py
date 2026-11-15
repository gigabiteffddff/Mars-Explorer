"""Points of interest and hazard zones. Add new ones here (lat, lon).

DEFAULT_SITES  - curated points, drawn on the map with labels.
SITES          - DEFAULT_SITES + the USGS/IAU catalogue (data/mars_features.json),
                 used for choosing the start / destinations of a route.
"""
import json
from pathlib import Path

from geo import offset_km

DEFAULT_SITES = {
    "Habitat Alpha": (-1.7, -0.2),
    "Western delta": (1.1, -1.7),
    "Olympus Mons": (18.65, -133.8),
    "Valles Marineris": (-13.9, -59.2),
}

JSON_PATH = Path(__file__).resolve().parent / "data" / "mars_features.json"


def _load_catalogue_sites():
    """name -> (lat, lon) from the catalogue. Never raises: a missing or
    broken file just means the route lists only DEFAULT_SITES."""
    try:
        records = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Catalogue not found: {JSON_PATH}")
        return {}
    except (OSError, ValueError) as error:
        print(f"Could not read catalogue: {error}")
        return {}

    found = {}
    for item in records:
        try:
            name = str(item["name"]).strip()
            point = (float(item["lat"]), float(item["lon"]))
        except (KeyError, TypeError, ValueError):
            continue  # skip a broken record, keep the rest
        if name and name not in DEFAULT_SITES:
            found[name] = point
    return dict(sorted(found.items(), key=lambda kv: kv[0].casefold()))


CATALOGUE_SITES = _load_catalogue_sites()  # runs once, at the first import
SITES = {**DEFAULT_SITES, **CATALOGUE_SITES}

# Demo base around the Jezero landing site; offsets are (north km, east km).
_JEZERO = (18.4447, 77.4508)


def _near_jezero(north_km, east_km):
    return offset_km(*_JEZERO, north_km, east_km)


# (lat, lon, radius_km) — simulated hazard zones, DEMO only
HAZARDS = [
    (*_near_jezero(1.8, 0.4), 0.6),
    (*_near_jezero(-2.5, 1.7), 0.6),
]
