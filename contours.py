"""Smooth iso-lines (contours) for the data layers, cached."""
import numpy as np
import streamlit as st
from contourpy import contour_generator

from config import CONTOUR_H, CONTOUR_W, LAYERS
from fields import sample


def _chaikin(points, rounds=1):
    """Round off the corners of an open polyline (ends stay in place)."""
    pts = np.asarray(points, dtype=float)
    for _ in range(rounds):
        if len(pts) < 3:
            break
        near = 0.75 * pts[:-1] + 0.25 * pts[1:]
        far = 0.25 * pts[:-1] + 0.75 * pts[1:]
        mid = np.empty((2 * len(near), 2))
        mid[0::2], mid[1::2] = near, far
        pts = np.vstack([pts[:1], mid, pts[-1:]])
    return pts


@st.cache_data
def contour_geojson(name):
    """GeoJSON FeatureCollection: one MultiLineString per contour level."""
    cfg = LAYERS[name]
    lon = np.linspace(-180, 180, CONTOUR_W)
    lat = np.linspace(-90, 90, CONTOUR_H)
    grid_lon, grid_lat = np.meshgrid(lon, lat)
    z = sample(grid_lat, grid_lon, fine=False)[cfg["field"]]

    # levels come from the configured range, but only those that really
    # occur in the data are used (an empty layer must never reach folium)
    lo, hi = cfg["range"]
    levels = np.linspace(lo, hi, cfg["contour_levels"] + 2)[1:-1]
    levels = levels[(levels > np.nanmin(z)) & (levels < np.nanmax(z))]
    generator = contour_generator(lon, lat, z)

    features = []
    for level in levels:
        lines = [
            np.round(_chaikin(line), 4).tolist()  # [[lon, lat], ...]
            for line in generator.lines(float(level))
            if len(line) >= 3
        ]
        if lines:
            features.append({
                "type": "Feature",
                "properties": {"level": round(float(level), 4)},
                "geometry": {"type": "MultiLineString", "coordinates": lines},
            })
    return {"type": "FeatureCollection", "features": features}
