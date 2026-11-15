import math

import numpy as np

from config import TRAVEL_SPEED_KMH
from geo import haversine_km
from local_navigator import a_star


MAX_SLOPE_DEG = 25.0

# Slope and radiation weights.
MODES = {
    "shortest": (0.0, 0.0),
    "balanced": (2.0, 2.0),
    "safe": (5.0, 6.0),
}


class GeoGrid:
    """Maps grid rows and columns to Mars coordinates."""

    def __init__(
        self,
        lat_top,
        lon_left,
        deg_lat_per_px,
        deg_lon_per_px,
        px_m,
    ):
        values = (
            lat_top,
            lon_left,
            deg_lat_per_px,
            deg_lon_per_px,
            px_m,
        )

        if (
            not all(math.isfinite(v) for v in values)
            or min(values[2:]) <= 0
        ):
            raise ValueError("Invalid geographic grid parameters")

        self.lat_top = lat_top
        self.lon_left = lon_left
        self.dlat = deg_lat_per_px
        self.dlon = deg_lon_per_px
        self.px_m = px_m

    def to_px(self, lat, lon):
        if (
            not math.isfinite(lat)
            or not math.isfinite(lon)
            or abs(lat) > 90
        ):
            raise ValueError("Invalid coordinates")

        # Closest longitude representation relative to the grid origin.
        lon = self.lon_left + (lon - self.lon_left + 180) % 360 - 180

        return (
            int(round((self.lat_top - lat) / self.dlat)),
            int(round((lon - self.lon_left) / self.dlon)),
        )

    def to_latlon(self, row, col):
        return (
            self.lat_top - row * self.dlat,
            self.lon_left + col * self.dlon,
        )


def build_cost(slope, radiation, hazard, mode="balanced"):
    if mode not in MODES:
        raise ValueError(f"Unknown navigation mode: {mode}")

    slope = np.asarray(slope, dtype=float)
    radiation = np.asarray(radiation, dtype=float)
    hazard = np.asarray(hazard, dtype=bool)

    if (
        slope.ndim != 2
        or slope.size == 0
        or slope.shape != radiation.shape
        or slope.shape != hazard.shape
    ):
        raise ValueError("Layers must be nonempty 2-D arrays with matching shapes")

    valid = (
        np.isfinite(slope)
        & np.isfinite(radiation)
        & (slope >= 0)
        & (radiation >= 0)
    )

    rad_ref = (
        max(float(np.median(radiation[valid])), 1e-9)
        if valid.any()
        else 1.0
    )

    slope_weight, radiation_weight = MODES[mode]

    with np.errstate(invalid="ignore", over="ignore"):
        cost = (
            1.0
            + slope_weight * (slope / MAX_SLOPE_DEG) ** 2
            + radiation_weight
            * np.clip(radiation / rad_ref - 1.0, 0, 5)
        )

    cost[
        ~valid
        | (slope > MAX_SLOPE_DEG)
        | hazard
    ] = np.inf

    return cost


def plan_route(
    geo,
    slope,
    radiation,
    hazard,
    start_ll,
    goal_ll,
    mode="balanced",
    margin_px=60,
    speed_kmh=TRAVEL_SPEED_KMH,
):
    """
    radiation: mGy/day.
    Result: coordinates, kilometres, hours and dose in mGy.
    """
    if not math.isfinite(speed_kmh) or speed_kmh <= 0:
        raise ValueError("Travel speed must be positive")

    if not isinstance(margin_px, int) or margin_px < 0:
        raise ValueError("margin_px must be a nonnegative integer")

    cost = build_cost(slope, radiation, hazard, mode)
    slope = np.asarray(slope)
    radiation = np.asarray(radiation)

    start = geo.to_px(*start_ll)
    goal = geo.to_px(*goal_ll)

    height, width = cost.shape

    for row, col in (start, goal):
        if not (0 <= row < height and 0 <= col < width):
            raise ValueError("Start or destination lies outside the navigation grid")

    if not np.isfinite(cost[start]) or not np.isfinite(cost[goal]):
        return None

    margin = margin_px

    while True:
        r0 = max(min(start[0], goal[0]) - margin, 0)
        r1 = min(max(start[0], goal[0]) + margin + 1, height)
        c0 = max(min(start[1], goal[1]) - margin, 0)
        c1 = min(max(start[1], goal[1]) + margin + 1, width)

        local_start = (start[0] - r0, start[1] - c0)
        local_goal = (goal[0] - r0, goal[1] - c0)

        def latlon(point):
            return geo.to_latlon(point[0] + r0, point[1] + c0)

        path, total = a_star(
            cost[r0:r1, c0:c1],
            local_start,
            local_goal,
            distance=lambda a, b: haversine_km(latlon(a), latlon(b)),
            heuristic=lambda p: haversine_km(
                latlon(p), latlon(local_goal)
            ),
        )

        full_grid = (
            r0 == 0
            and c0 == 0
            and r1 == height
            and c1 == width
        )

        if path is not None or full_grid:
            break

        margin = max(1, margin * 2)

    if path is None:
        return None

    pixels = [(row + r0, col + c0) for row, col in path]
    coords = [geo.to_latlon(*point) for point in pixels]

    lengths = [
        haversine_km(a, b)
        for a, b in zip(coords, coords[1:])
    ]

    length_km = sum(lengths)

    dose_mgy = sum(
        (float(radiation[a]) + float(radiation[b]))
        / 2
        * distance_km
        / speed_kmh
        / 24
        for a, b, distance_km in zip(
            pixels, pixels[1:], lengths
        )
    )

    return {
        "mode": mode,
        "coords": coords,
        "length_km": length_km,
        "time_h": length_km / speed_kmh,
        "dose_mgy": dose_mgy,
        "max_slope_deg": max(float(slope[p]) for p in pixels),
        "weighted_cost": total,
    }


def compare_modes(
    geo,
    slope,
    radiation,
    hazard,
    start_ll,
    goal_ll,
    **kwargs,
):
    return {
        mode: plan_route(
            geo,
            slope,
            radiation,
            hazard,
            start_ll,
            goal_ll,
            mode=mode,
            **kwargs,
        )
        for mode in MODES
    }