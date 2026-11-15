"""Planet-wide fields.
elevation, slope  - real MOLA topography (16 pixels/degree, ~3.7 km)
radiation         - simple model: GCR dose vs atmospheric column depth,
                    calibrated on Curiosity/RAD at Gale crater (mGy/day)
temperature       - real Mars Climate Database (MCD) surface temperature map
                    for a FIXED season/time (see TEMP_NOTE), from data/tsurf.txt.
                    Falls back to a synthetic field if the file is missing.

The MOLA file (~33 MB) is downloaded automatically on first use and kept in
data/. If that is impossible (no internet), elevation falls back to a
synthetic field, so the app never crashes.
Manual download: python fields.py --download

Temperature file: download it from the MCD web interface
(https://www-mars.lmd.jussieu.fr/mcd_python/index.html):
  variable = surface temperature (tsurf), Ls = 0, Local Time = 12,
  latitude = all, longitude = all, "same LT on whole planet" = on,
  save the text output -> data/tsurf.txt

sample(lat, lon) works for scalars or numpy arrays.
"""
import shutil
import sys
import urllib.request
from pathlib import Path

import numpy as np

from config import LAYERS

DATA_DIR = Path(__file__).resolve().parent / "data"

# ---------- DEM (MOLA MEGDR, 16 ppd, 0..360E, 90N..90S, int16 big-endian) ----------
DEM_PATH = DATA_DIR / "megt90n000eb.img"
DEM_W, DEM_H = 5760, 2880
DEM_BYTES = DEM_W * DEM_H * 2                 # 33 177 600
AUTO_DOWNLOAD = True                          # fetch the file if it is missing
REQUIRE_REAL_DEM = False                      # True = error instead of synthetic fallback
DEM_URLS = [                                  # tried in this order
    "https://pds-geosciences.wustl.edu/mgs/urn-nasa-pds-mgs_mola_topography_derived/meg016/megt90n000eb.img",
    "https://pds-geosciences.wustl.edu/mgs/mgs-m-mola-5-megdr-l3-v1/mgsl_300x/meg016/megt90n000eb.img",
]
R_KM = 3396.0
PIXEL_KM = 2 * np.pi * R_KM / DEM_W          # ~3.7 km

# ---------- temperature (MCD surface temperature, fixed time) ----------
TEMP_PATH = DATA_DIR / "tsurf.txt"
TEMP_NOTE = "MCD, Ls=0, local time 12:00 across the whole planet"

# ---------- radiation model ----------
SCALE_HEIGHT_KM = 11.1   # atmosphere scale height (approx.)
COLUMN_0 = 16.4          # g/cm2 at MOLA 0 m (~610 Pa / g), approx.
GALE_ELEV_M = -4400.0
GALE_DOSE = 0.21         # mGy/day, Curiosity RAD measurement (GCR)
SPACE_DOSE = 0.48        # mGy/day, upper cap (~cruise level)
K = 0.4                  # ASSUMED sensitivity to column depth

ADD_FINE_DETAIL = True   # tiny synthetic ripples so routes of a few km are not flat

_dem = None
_temp = None


# =====================================================================
#  DEM
# =====================================================================
def download_dem(force=False):
    """Download the MOLA 16 ppd topography once. Returns True on success."""
    if not force and DEM_PATH.exists() and DEM_PATH.stat().st_size == DEM_BYTES:
        return True
    DEM_PATH.parent.mkdir(parents=True, exist_ok=True)
    part = DEM_PATH.with_suffix(".part")
    for url in DEM_URLS:
        try:
            print(f"DEM: downloading {url} ...")
            request = urllib.request.Request(
                url, headers={"User-Agent": "mars-explorer/1.0"})
            with urllib.request.urlopen(request, timeout=60) as src, \
                    open(part, "wb") as dst:
                shutil.copyfileobj(src, dst, 1 << 20)
            if part.stat().st_size != DEM_BYTES:
                print(f"DEM: wrong size ({part.stat().st_size} bytes, "
                      f"expected {DEM_BYTES}), trying the next link")
                continue
            part.replace(DEM_PATH)
            print(f"DEM: saved {DEM_PATH}")
            return True
        except Exception as error:  # noqa: BLE001 - network can fail in many ways
            print(f"DEM: failed ({error})")
    part.unlink(missing_ok=True)
    return False


def _read_dem():
    """float32 array (DEM_H, DEM_W) in metres, or None if unusable."""
    if not DEM_PATH.exists() and AUTO_DOWNLOAD:
        download_dem()
    if not DEM_PATH.exists():
        print(f"DEM: file not found {DEM_PATH}, using synthetic elevation")
        return None
    raw = np.fromfile(DEM_PATH, dtype=">i2")
    if raw.size != DEM_W * DEM_H:
        print(f"DEM: wrong file size for {DEM_PATH} "
              f"({raw.size} values, expected {DEM_W * DEM_H}). "
              "Delete it to download it again.")
        return None
    dem = raw.reshape(DEM_H, DEM_W).astype(np.float32)
    if dem.min() < -9000 or dem.max() > 22000:   # real MOLA: -8177 .. 21171 m
        print("DEM: values outside the MOLA range; the file is corrupted or in the wrong format")
        return None
    return dem


def _load_dem():
    """Loaded once per process (the result is cached, also when it is None)."""
    global _dem
    if _dem is None:
        dem = _read_dem()
        if dem is None and REQUIRE_REAL_DEM:
            raise RuntimeError(
                f"No real MOLA DEM available. Put megt90n000eb.img in {DEM_PATH.parent}")
        _dem = dem if dem is not None else False
    return _dem if _dem is not False else None


def dem_loaded():
    """True if real MOLA elevation is used, False for the synthetic fallback."""
    return _load_dem() is not None


# =====================================================================
#  Temperature (MCD)
# =====================================================================
def _read_temp():
    """(lats, lons, grid in deg C) from an MCD text export, or None.

    Format: '#' header lines; a line '---- || lat1 lat2 ...';
    then one line per longitude: 'lon  T(lat1) T(lat2) ...' (Kelvin).
    """
    if not TEMP_PATH.exists():
        print(f"TEMP: file not found {TEMP_PATH}, using synthetic temperature")
        return None
    try:
        lats = None
        lons, rows = [], []
        with open(TEMP_PATH, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                if not s.strip("-|= "):          # separator line like '------'
                    continue
                if "||" in s and s.split("||")[0].strip("- ") == "":
                    lats = np.array(s.split("||")[1].split(), dtype=float)
                    continue
                values = [float(p) for p in s.replace("||", " ").split()]
                lons.append(values[0])
                rows.append(values[1:])
        if lats is None:
            raise ValueError("latitude row ('---- ||') not found")
        if not rows or any(len(r) != lats.size for r in rows):
            raise ValueError("number of values per row does not match the number of latitudes")
        lons = np.array(lons, dtype=float) % 360
        grid = np.array(rows, dtype=float).T            # (lat, lon)
        if not np.isfinite(grid).any():
            raise ValueError("no numbers in the file")
        grid = np.where(np.isfinite(grid), grid, np.nanmean(grid))
    except Exception as error:  # noqa: BLE001
        print(f"TEMP: could not read ({error}), using synthetic temperature")
        return None
    if grid.mean() > 150:                      # Kelvin -> deg C
        grid = grid - 273.15
    order = np.argsort(lats)
    lats, grid = lats[order], grid[order]
    order = np.argsort(lons)
    lons, grid = lons[order], grid[:, order]
    lons = np.append(lons, lons[0] + 360)      # wrap around in longitude
    grid = np.concatenate([grid, grid[:, :1]], axis=1)
    return lats, lons, grid


def _load_temp():
    """Loaded once per process (cached, also when it is None)."""
    global _temp
    if _temp is None:
        data = _read_temp()
        _temp = data if data is not None else False
    return _temp if _temp is not False else None


def temp_loaded():
    """True if the real MCD temperature map is used."""
    return _load_temp() is not None


def _real_temperature(lat, lon):
    data = _load_temp()
    if data is None:
        return None
    lats, lons, grid = data
    lat = np.clip(np.asarray(lat, dtype=float), lats[0], lats[-1])
    lon = np.asarray(lon, dtype=float) % 360
    lon = np.where(lon < lons[0], lon + 360, lon)
    i = np.clip(np.searchsorted(lats, lat) - 1, 0, lats.size - 2)
    j = np.clip(np.searchsorted(lons, lon) - 1, 0, lons.size - 2)
    fy = (lat - lats[i]) / (lats[i + 1] - lats[i])
    fx = np.clip((lon - lons[j]) / (lons[j + 1] - lons[j]), 0, 1)
    top = grid[i, j] * (1 - fx) + grid[i, j + 1] * fx
    bot = grid[i + 1, j] * (1 - fx) + grid[i + 1, j + 1] * fx
    return top * (1 - fy) + bot * fy


def _temperature(lat, lon, fine):
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    real = _real_temperature(lat, lon)
    if real is not None:
        return real                            # real data: no fake ripples
    la, lo = np.radians(lat), np.radians(lon)
    t = -34 - 36 * (np.abs(lat) / 90) ** 1.2 + 6 * np.sin(3 * lo + 2 * la)
    if fine:
        t = t + 3 * _wave(lon + lat, 0.3)
    return t


# =====================================================================
#  Layers
# =====================================================================
def layer_tag(name):
    """What a data layer really is: 'MOLA', 'model' or 'DEMO'."""
    cfg = LAYERS[name]
    needs_dem = cfg["field"] in ("elevation", "slope", "radiation")
    if needs_dem and not dem_loaded():
        return "DEMO"
    if cfg["field"] == "temperature" and not temp_loaded():
        return "DEMO"
    return cfg.get("tag", "DEMO")


def _wave(deg, wavelength_deg):
    return np.sin(2 * np.pi * np.asarray(deg, dtype=float) / wavelength_deg)


def _synthetic_elevation(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return (1000
            + 3500 * np.sin(2 * lo + 0.5) * np.cos(2 * la)
            + 1200 * np.sin(5 * lo) * np.cos(4 * la))


def _base_elevation(lat, lon):
    lat = np.clip(np.asarray(lat, dtype=float), -90, 90)
    lon = np.asarray(lon, dtype=float)
    dem = _load_dem()
    if dem is None:
        return _synthetic_elevation(lat, lon)
    x = (lon % 360) / 360 * DEM_W - 0.5
    y = (90 - lat) / 180 * DEM_H - 0.5
    x0 = np.floor(x).astype(int)
    y0 = np.floor(y).astype(int)
    fx, fy = x - x0, y - y0
    xa, xb = x0 % DEM_W, (x0 + 1) % DEM_W
    ya = np.clip(y0, 0, DEM_H - 1)
    yb = np.clip(y0 + 1, 0, DEM_H - 1)
    top = dem[ya, xa] * (1 - fx) + dem[ya, xb] * fx
    bot = dem[yb, xa] * (1 - fx) + dem[yb, xb] * fx
    return top * (1 - fy) + bot * fy


def _base_slope(lat, lon):
    lat = np.asarray(lat, dtype=float)
    d = np.degrees(PIXEL_KM / R_KM)
    dlon = d / np.maximum(np.cos(np.radians(lat)), 0.05)
    dz_dy = (_base_elevation(lat + d, lon) - _base_elevation(lat - d, lon)) / (2 * PIXEL_KM * 1000)
    dz_dx = (_base_elevation(lat, lon + dlon) - _base_elevation(lat, lon - dlon)) / (2 * PIXEL_KM * 1000)
    return np.degrees(np.arctan(np.hypot(dz_dx, dz_dy)))


def column_g_cm2(elev_m):
    return COLUMN_0 * np.exp(-np.asarray(elev_m, dtype=float) / 1000 / SCALE_HEIGHT_KM)


def radiation_mgy_day(elev_m):
    ratio = column_g_cm2(GALE_ELEV_M) / column_g_cm2(elev_m)   # = 1 at Gale
    return np.minimum(GALE_DOSE * ratio ** K, SPACE_DOSE)


def sample(lat, lon, fine=True):
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    elev = _base_elevation(lat, lon)
    radiation = radiation_mgy_day(elev)          # from the real (smooth) elevation
    slope = _base_slope(lat, lon)
    if fine and ADD_FINE_DETAIL:
        elev = elev + 120 * _wave(lon, 0.2) * _wave(lat, 0.17)
        slope = slope + 13 * np.abs(_wave(lon, 0.3) * _wave(lat, 0.25))
    return {
        "radiation": radiation,
        "temperature": _temperature(lat, lon, fine),
        "elevation": elev,
        "slope": slope,
    }


if __name__ == "__main__":   # python fields.py [--download]
    if "--download" in sys.argv:
        download_dem(force=True)
    print("MOLA loaded:", dem_loaded())
    print("MCD temperature loaded:", temp_loaded(),
          f"({TEMP_NOTE})" if temp_loaded() else "")
    for name, (la, lo) in {
        "Olympus Mons": (18.65, -133.8),   # ~ +21 km
        "Gale crater": (-5.4, 137.8),      # ~ -4.4 km
        "Hellas": (-42.0, 70.0),           # ~ -7 km
    }.items():
        s = sample(la, lo, fine=False)
        print(name, round(float(s["elevation"])), "m,",
              round(float(s["radiation"]), 3), "mGy/day,",
              round(float(s["temperature"]), 1), "°C")