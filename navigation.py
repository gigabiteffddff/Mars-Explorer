import json
import math

import numpy as np

from config import MARS_RADIUS_KM, TRAVEL_SPEED_KMH
from fields import sample
from geo import KM_PER_DEG, haversine_km, wrap_lon
from i18n import translate
from route_planner import GeoGrid, plan_route
from sites import HAZARDS


MAX_LEG_KM = 1000


class RouteError(ValueError):
    """A route problem the user can fix; app.py shows it in their language."""

    def __init__(self, key, **params):
        super().__init__(translate(key, "en", **params))
        self.key = key
        self.params = params


def _grid(a, b, resolution_m):
    if (
        haversine_km(a, b) > MAX_LEG_KM
        or max(abs(a[0]), abs(b[0])) > 80
    ):
        raise RouteError("err.legs_range")

    # Short hop across ±180°.
    b = (b[0], a[1] + wrap_lon(b[1] - a[1]))

    cos_lat = max(
        math.cos(math.radians((a[0] + b[0]) / 2)),
        0.1,
    )

    # Limit the number of nodes by increasing the step for long legs.
    target_km = max(
        resolution_m / 1000,
        abs(a[0] - b[0]) * KM_PER_DEG / 200,
        abs(a[1] - b[1]) * KM_PER_DEG * cos_lat / 200,
    )

    def axis(v1, v2, km_per_deg):
        span = abs(v1 - v2)
        count = max(1, math.ceil(span * km_per_deg / target_km))

        step = (
            span / count
            if span > 1e-12
            else target_km / km_per_deg
        )

        padding = max(12, math.ceil(count * 0.2))
        size = (count if span > 1e-12 else 0) + 2 * padding + 1

        return step, padding, size

    dlat, row_padding, height = axis(
        a[0], b[0], KM_PER_DEG
    )
    dlon, col_padding, width = axis(
        a[1], b[1], KM_PER_DEG * cos_lat
    )

    geo = GeoGrid(
        lat_top=max(a[0], b[0]) + row_padding * dlat,
        lon_left=min(a[1], b[1]) - col_padding * dlon,
        deg_lat_per_px=dlat,
        deg_lon_per_px=dlon,
        px_m=target_km * 1000,
    )

    lon, lat = np.meshgrid(
        geo.lon_left + np.arange(width) * dlon,
        geo.lat_top - np.arange(height) * dlat,
    )

    values = sample(lat, wrap_lon(lon))
    hazards = np.zeros((height, width), dtype=bool)

    # Margin around zones for edges between nodes.
    clearance_km = math.hypot(
        dlat * KM_PER_DEG,
        dlon * KM_PER_DEG * cos_lat,
    ) / 2

    for hazard_lat, hazard_lon, radius_km in HAZARDS:
        dy = np.radians(lat - hazard_lat)
        dx = np.radians(wrap_lon(lon - hazard_lon))

        hav = (
            np.sin(dy / 2) ** 2
            + np.cos(np.radians(lat))
            * math.cos(math.radians(hazard_lat))
            * np.sin(dx / 2) ** 2
        )

        distance = (
            2
            * MARS_RADIUS_KM
            * np.arcsin(np.sqrt(np.clip(hav, 0, 1)))
        )

        hazards |= distance <= radius_km + clearance_km

        for point in (a, b):
            if haversine_km(
                point, (hazard_lat, hazard_lon)
            ) <= radius_km:
                raise RouteError("err.in_hazard")

    return geo, values, hazards, a, b, target_km * 1000


def navigate(
    points,
    mode="balanced",
    resolution_m=250,
    speed_kmh=TRAVEL_SPEED_KMH,
):
    """Builds a route through all points in the given order."""
    if len(points) < 2:
        return None

    if not math.isfinite(resolution_m) or resolution_m <= 0:
        raise RouteError("err.grid_positive")

    coords = []
    legs = []
    leg_details = []
    resolutions = []

    for index, (a, b) in enumerate(
        zip(points, points[1:]), start=1
    ):
        geo, values, hazards, a, b, actual_resolution = _grid(
            a, b, resolution_m
        )

        result = plan_route(
            geo,
            values["slope"],
            values["radiation"],
            hazards,
            a,
            b,
            mode=mode,
            margin_px=max(hazards.shape),
            speed_kmh=speed_kmh,
        )

        if result is None:
            raise RouteError("err.no_route", index=index)

        leg = result["coords"]

        if coords:
            shift = 360 * round(
                (coords[-1][1] - leg[0][1]) / 360
            )
            leg = [
                (lat, lon + shift)
                for lat, lon in leg
            ]

        coords.extend(leg if not coords else leg[1:])
        legs.append(result)
        leg_details.append(
            {
                "distance_km": result["length_km"],
                "minutes": result["time_h"] * 60,
            }
        )
        resolutions.append(actual_resolution)

    return {
        "coords": coords,
        "mode": mode,
        "distance_km": sum(r["length_km"] for r in legs),
        "minutes": sum(r["time_h"] for r in legs) * 60,
        "dose_mgy": sum(r["dose_mgy"] for r in legs),
        "max_slope_deg": max(
            r["max_slope_deg"] for r in legs
        ),
        "grid_m": max(resolutions),
        "legs": len(legs),
        "speed_kmh": speed_kmh,
        "leg_details": leg_details,
    }


def geojson_route(result):
    """Export with the line split at the ±180° boundary."""
    lines = [[]]

    for lat, lon in result["coords"]:
        point = [wrap_lon(lon), lat]
        previous = lines[-1][-1] if lines[-1] else None

        if previous and abs(point[0] - previous[0]) > 180:
            unwrapped = previous[0] + wrap_lon(
                point[0] - previous[0]
            )
            edge = (
                180
                if point[0] - previous[0] < -180
                else -180
            )

            fraction = (
                (edge - previous[0])
                / (unwrapped - previous[0])
            )
            crossing_lat = previous[1] + fraction * (
                lat - previous[1]
            )

            lines[-1].append([edge, crossing_lat])
            lines.append([[-edge, crossing_lat]])

        lines[-1].append(point)

    if len(result["coords"]) == 1:
        geometry = {
            "type": "Point",
            "coordinates": lines[0][0],
        }
    else:
        geometry = {
            "type": "MultiLineString",
            "coordinates": lines,
        }

    return json.dumps(
        {
            "type": "Feature",
            "properties": {
                key: value
                for key, value in result.items()
                if key != "coords"
            },
            "geometry": geometry,
        },
        ensure_ascii=False,
    )