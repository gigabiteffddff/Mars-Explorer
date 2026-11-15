"""Route statistics along straight lat/lon segments (as drawn on the map)."""
import numpy as np

from config import TRAVEL_SPEED_KMH
from fields import sample
from geo import haversine_km


def route_statistics(points):
    """points: list of (lat, lon). Returns a dict, or None for < 2 points."""
    if len(points) < 2:
        return None

    distance_km = 0.0
    chunks = []
    for a, b in zip(points, points[1:]):
        n = int(np.clip(haversine_km(a, b) / 0.25, 10, 2000))
        lats = np.linspace(a[0], b[0], n)
        lons = np.linspace(a[1], b[1], n)
        distance_km += sum(
            haversine_km((lats[i], lons[i]), (lats[i + 1], lons[i + 1]))
            for i in range(n - 1)
        )
        chunks.append(sample(lats, lons))

    def joined(key):
        return np.concatenate([c[key] for c in chunks])

    hours = distance_km / TRAVEL_SPEED_KMH
    return {
        "distance_km": distance_km,
        "minutes": hours * 60,
        # radiation is mGy/day, so dose = mean rate * days spent on the route
        "dose_mgy": float(joined("radiation").mean()) * hours / 24,
        "temperature_c": float(joined("temperature").mean()),
        "max_slope_deg": float(joined("slope").max()),
    }
