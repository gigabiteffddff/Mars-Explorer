"""Constants only, no logic. Change look, layers, ranges and speeds here.

Conventions used everywhere in this project:
  * positions are (lat, lon) in decimal degrees, lon -180..180, east positive
  * distances are km, speeds km/h
"""

PAGE_TITLE = "Velvet Space Underground Lab"
START_VIEW = (18.4447, 77.4508, 9)  # lat, lon, zoom of the first screen

MARS_RADIUS_KM = 3396.19  # the sphere NASA Trek tiles are built on
TRAVEL_SPEED_KMH = 3.0

# --- imagery: NASA Mars Trek WMTS tiles (equirectangular = Leaflet EPSG4326)
TREK_URL = (
    "https://trek.nasa.gov/tiles/Mars/EQ/{layer}/1.0.0/"
    "default/default028mm/{{z}}/{{y}}/{{x}}.{ext}"
)

# Global base maps (cover the whole planet).
# name -> (Trek layer id, deepest zoom that really has tiles)
BASEMAPS = {
    "Viking colour mosaic (232 m/px)": (
        "Mars_Viking_MDIM21_ClrMosaic_global_232m", 7),
    "MOLA colour shaded relief (463 m/px)": (
        "Mars_MGS_MOLA_ClrShade_merge_global_463m", 6),
}

# Sharper regional mosaics drawn ON TOP of the base while zooming in.
# (name, Trek layer id, file ext, first zoom shown, deepest zoom,
#  coverage [[south, west], [north, east]])
# Blank at deep zoom? Check id / ext at
# https://trek.nasa.gov/tiles/apidoc/trekAPI.html?body=mars
HIRES_LAYERS = [
    ("MRO CTX Jezero (~6 m/px)", "Jezero_CTX_BlockAdj_dd", "jpg", 7, 12,
     [[16.0, 76.0], [20.0, 80.0]]),
    ("MRO HiRISE Jezero (25 cm/px)",
     "JEZ_hirise_soc_006_orthoMosaic_25cm_Eqc_latTs0_lon0_first_dd",
     "jpg", 11.5, 17,
     [[18.3068, 77.2229], [18.6693, 77.5840]]),
]

# --- data layers
# To add a layer: add an entry here and a matching key in fields.sample().
# field:          key returned by fields.sample()
# range/unit:     colour scale of the raster and the contour levels
# tag:            what the data really is (shown in the UI). If the MOLA DEM
#                 file is missing, fields.layer_tag() downgrades it to "DEMO".
# contour_color:  dark colour of that layer's contour lines
# contour_levels: how many lines across the value range
LAYERS = {
    "Radiation": {
        # modelled GCR dose, calibrated on Curiosity/RAD (see fields.py)
        "field": "radiation", "range": (0.18, 0.40), "unit": "mGy/day",
        "tag": "model",
        "palette": ["#52c392", "#e4ca67", "#e66a51"],
        "contour_color": "#5b1a8c",  # dark violet
        "contour_levels": 9,
    },
    "Temperature": {
        "field": "temperature", "range": (-76, -28), "unit": "°C",
        "tag": "DEMO",
        "palette": ["#4b8cdb", "#eab658", "#e96047"],
        "contour_color": "#0a2a5e",  # dark navy
        "contour_levels": 9,
    },
    "Terrain": {
        # real MOLA topography (16 pixels/degree)
        "field": "elevation", "range": (-6000, 8000), "unit": "m",
        "tag": "MOLA",
        "palette": ["#4d6577", "#a59070", "#d8c4a0"],
        "contour_color": "#4a2c0a",  # dark brown
        "contour_levels": 9,
    },
}

# Resolution of the planet-wide overlay rasters (plate carrée, 360° x 180°)
GRID_W, GRID_H = 1024, 512

# Contour lines: finer grid = smoother lines.
CONTOUR_W, CONTOUR_H = 1440, 720
CONTOUR_WEIGHT = 1.3
CONTOUR_OPACITY = 0.85

START_COLOR = "#4b8cdb"
STOP_COLOR = "#e98c59"
HAZARD_COLOR = "#f26b56"
ROUTE_COLOR = "#ffad76"