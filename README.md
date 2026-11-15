# Mars Explorer (Streamlit demo)

Run: `pip install -r requirements.txt && streamlit run app.py`
(or `python run_mars.py`)

Conventions: positions are `(lat, lon)` in degrees, lon -180..180 (east +),
distances in km.

## What is real and what is not
| Data | Source |
|------|--------|
| Base imagery | NASA Mars Trek tiles (needs internet) |
| Elevation, slope | MOLA topography, 16 px/degree (~3.7 km) - needs `data/megt90n000eb.img` |
| Temperature | Mars Climate Database (MCD), LMD Paris: https://www-mars.lmd.jussieu.fr/mcd_python/index.html |
| Radiation | simple MODEL: GCR dose vs atmospheric column depth (from elevation), calibrated on Curiosity/RAD at Gale (0.21 mGy/day). No solar events, seasons, dust |
| Place names | USGS/IAU catalogue `data/mars_features.json` |
| Hazard zones, Jezero sites | synthetic DEMO |

## MOLA elevation file (one-time, ~33 MB)
Download `megt90n000eb.img` (MOLA MEGDR, 16 pixels/degree, topography) from the
MEG016 folder of https://pds-geosciences.wustl.edu/missions/mgs/megdr.html
and put it in `data/`. Without it the app still runs, but elevation, slope and
radiation are synthetic and the UI says "DEMO". Restart Streamlit after adding it.
Check the file with `python fields.py` (Olympus ~ +21000 m, Gale ~ -4400 m).

## Where to change what (each file is small and independent)
| I want to...                             | Edit              |
|------------------------------------------|-------------------|
| change colours, ranges, speeds, tile ids | `config.py`       |
| add a data layer (e.g. dust)             | `config.LAYERS` + a key in `fields.sample()` |
| change radiation model / data            | `fields.py`       |
| add a site or hazard zone                | `sites.py`        |
| add a map layer / control                | `map_layers.py` (one function per layer, call it in `app.py`) |
| add a sidebar widget                     | `sidebar.py` (add a field to `Settings`) |
| change route maths                       | `route.py`        |
| change the info panel or footer          | `panels.py`       |
| distances, circles, longitude wrapping   | `geo.py`          |
| USGS place-name layer / catalogue        | `mars_geo.py` (`python mars_geo.py` re-downloads the catalogue) |
| change or add interface translations     | `i18n.py` (one dict per language) |

`app.py` only wires the pieces together.

Note: when you change the radiation range in `config.LAYERS`, contour levels
follow automatically (only levels that exist in the data are drawn).
