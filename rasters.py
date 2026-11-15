"""Planet-wide colour rasters for the data layers (cached)."""
import numpy as np
import streamlit as st

from config import GRID_H, GRID_W, LAYERS
from fields import sample


def colorize(field, hex_colors):
    """Map values in 0..1 onto a multi-stop colour ramp -> uint8 RGB."""
    stops = np.linspace(0, 1, len(hex_colors))
    rgb = np.array(
        [[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in hex_colors]
    )
    field = np.clip(field, 0, 1)
    channels = [np.interp(field, stops, rgb[:, k]) for k in range(3)]
    return np.dstack(channels).astype(np.uint8)


@st.cache_data
def overlay_images():
    """One RGB image per layer covering lon -180..180, lat 90..-90."""
    lon, lat = np.meshgrid(
        np.linspace(-180, 180, GRID_W),
        np.linspace(90, -90, GRID_H),  # row 0 = north edge
    )
    values = sample(lat, lon, fine=False)
    images = {}
    for name, cfg in LAYERS.items():
        lo, hi = cfg["range"]
        images[name] = colorize(
            (values[cfg["field"]] - lo) / (hi - lo), cfg["palette"]
        )
    return images
