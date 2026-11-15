"""Pure geometry helpers. No Streamlit/folium imports."""
import math

from config import MARS_RADIUS_KM

KM_PER_DEG = 2 * math.pi * MARS_RADIUS_KM / 360


def wrap_lon(lon):
    """Bring any longitude into -180..180."""
    return (lon + 180) % 360 - 180


def haversine_km(a, b):
    """Great-circle distance between two (lat, lon) points on Mars."""
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = (
        math.sin((la2 - la1) / 2) ** 2
        + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    )
    return 2 * MARS_RADIUS_KM * math.asin(min(1.0, math.sqrt(h)))


def offset_km(lat, lon, north_km, east_km):
    """Point `north_km` / `east_km` away from (lat, lon) (small distances)."""
    dlat = north_km / KM_PER_DEG
    dlon = east_km / (KM_PER_DEG * max(math.cos(math.radians(lat)), 1e-6))
    return lat + dlat, lon + dlon


def circle_points(lat, lon, radius_km, n=48):
    """Outline of a circle as (lat, lon) points (folium.Circle assumes Earth)."""
    return [
        offset_km(
            lat, lon,
            radius_km * math.sin(2 * math.pi * k / n),
            radius_km * math.cos(2 * math.pi * k / n),
        )
        for k in range(n)
    ]
