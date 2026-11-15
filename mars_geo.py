import json
import math
import re
import time
import xml.etree.ElementTree as ET

from collections import Counter
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile

import streamlit as st
from branca.element import MacroElement, Template
from folium.plugins import MarkerCluster

from i18n import label, t


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DATA_FILE = DATA_DIR / "mars_features.json"
META_FILE = DATA_DIR / "mars_features.meta.json"

SOURCE_URL = (
    "https://asc-planetarynames-data.s3.us-west-2.amazonaws.com/"
    "MARS_nomenclature_center_pts.kmz"
)

NS = {"k": "http://www.opengis.net/kml/2.2"}

CATEGORIES = {
    "Craters": {"AA", "CA"},
    "Mountains": {"MO", "TH", "PE"},
    "Valleys": {"VA", "CM", "LB"},
    "Hills and Ridges": {"CO", "DO", "SU"},
    "Other features": set(),
}

# All display thresholds are collected here.
DISPLAY = {
    "size_rules": [
        (500, 0),
        (150, 2),
        (50, 4),
        (10, 6),
        (0, 8),
    ],
    "marker_limits": [
        (0, 40),
        (3, 200),
        (6, 700),
        (9, 2500),
    ],
    "label_limits": [
        (0, 6),
        (3, 12),
        (5, 24),
        (8, 45),
        (11, 80),
    ],
    "cluster_radius": 38,
    "cluster_disable_zoom": 9,
    "search_zoom": 7,
    "debounce_ms": 120,
}

# Documented overview landmarks from your reference screenshots.
# Jezero has the highest mission-area priority.
PRIORITIES = {
    "14300": 100,  # Jezero
    "4453": 50,    # Olympus Mons
    "6288": 50,    # Valles Marineris
    "2432": 50,    # Hellas Planitia
    "371": 50,     # Argyre Planitia
    "2071": 50,    # Gale
}


def feature_category(code):
    for name, codes in CATEGORIES.items():
        if code in codes:
            return name
    return "Other features"


def download_catalogue():
    """Download official USGS Mars data and create local JSON."""
    request = Request(
        SOURCE_URL,
        headers={"User-Agent": "VelvetSpace-MarsExplorer/1.0"},
    )

    with urlopen(request, timeout=45) as response:
        archive_bytes = response.read()

    with ZipFile(BytesIO(archive_bytes)) as archive:
        kml_name = next(
            name for name in archive.namelist()
            if name.lower().endswith(".kml")
        )
        root = ET.fromstring(archive.read(kml_name))

    records = {}
    duplicates = 0

    for placemark in root.findall(".//k:Placemark", NS):
        fields = {
            item.attrib["name"]: (item.text or "").strip()
            for item in placemark.findall(".//k:SimpleData", NS)
        }

        if fields.get("approval") != "Adopted by IAU":
            continue

        match = re.search(
            r"/Feature/(\d+)",
            fields.get("link", ""),
        )
        if not match:
            raise ValueError("An official USGS Feature ID is missing")

        feature_id = match.group(1)
        name = (
            placemark.findtext("k:name", namespaces=NS) or ""
        ).strip()

        lat = float(fields["center_lat"])
        lon_original = float(fields["center_lon"])

        if not (
            name
            and math.isfinite(lat)
            and math.isfinite(lon_original)
            and -90 <= lat <= 90
            and 0 <= lon_original <= 360
        ):
            raise ValueError(f"Invalid USGS coordinates: {name}")

        lon = (lon_original + 180) % 360 - 180
        diameter = float(fields.get("diameter") or 0)

        if not math.isfinite(diameter) or diameter < 0:
            raise ValueError(f"Invalid USGS size: {name}")

        code = fields["code"]

        record = {
            "id": feature_id,
            "name": name,
            "type": fields["type"].split(",", 1)[0],
            "type_code": code,
            "category": feature_category(code),
            "lat": lat,
            "lon": round(lon, 10),
            "diameter_km": diameter,
            "source": "USGS/IAU",
        }

        if feature_id in records:
            if records[feature_id] != record:
                raise ValueError(
                    f"Conflicting duplicate USGS ID: {feature_id}"
                )
            duplicates += 1
        else:
            records[feature_id] = record

    features = sorted(
        records.values(),
        key=lambda feature: int(feature["id"]),
    )

    if not features:
        raise ValueError("The USGS catalogue contains no usable records")

    metadata = {
        "source_url": SOURCE_URL,
        "catalogue_url": (
            "https://planetarynames.wr.usgs.gov/GIS_Downloads"
        ),
        "retrieved_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "body": "Mars",
        "latitude_type": "planetocentric",
        "longitude_direction": "positive_east",
        "longitude_range": [-180, 180],
        "control_network": "MDIM 2.1",
        "position_type": "catalogue_feature_center",
        "count": len(features),
        "duplicates_removed": duplicates,
        "category_counts": dict(
            Counter(feature["category"] for feature in features)
        ),
        "notes": [
            "Catalogue centres are not landing sites or mountain summits.",
            "diameter_km is approximate diameter or longest dimension.",
            "Category grouping describes browsing groups, not geological origin.",
            "Scientific environmental overlays remain DEMO.",
        ],
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    DATA_FILE.write_text(
        json.dumps(
            features,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ),
        encoding="utf-8",
    )

    META_FILE.write_text(
        json.dumps(
            metadata,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        ),
        encoding="utf-8",
    )

    return features


@st.cache_data(show_spinner=False)
def _read_catalogue(path, modified):
    return json.loads(
        Path(path).read_text(encoding="utf-8")
    )


def load_catalogue():
    if not DATA_FILE.exists():
        raise FileNotFoundError(t("geo.run_download"))

    return _read_catalogue(
        str(DATA_FILE),
        DATA_FILE.stat().st_mtime_ns,
    )


def geographic_sidebar():
    """Independent controls; does not touch scientific-layer state."""
    with st.sidebar:
        st.divider()
        st.header(t("geo.header"))

        try:
            features = load_catalogue()
        except (OSError, ValueError) as error:
            st.warning(str(error))
            return None

        enabled = st.checkbox(
            t("geo.show_all"),
            value=True,
            key="usgs_enabled",
        )

        selected_categories = [
            category
            for category in CATEGORIES
            if st.checkbox(
                label("category", category),
                value=True,
                key=f"usgs_category_{category}",
                disabled=not enabled,
            )
        ]

        labels = st.checkbox(
            t("geo.show_labels"),
            value=True,
            key="usgs_labels",
            disabled=not enabled,
        )

        available = {
            feature["id"]: feature
            for feature in features
            if feature["category"] in selected_categories
        }

        ids = sorted(
            available,
            key=lambda item: available[item]["name"].casefold(),
        )

        selected_id = st.selectbox(
            t("geo.search"),
            options=ids,
            key="usgs_search",
            index=None,
            format_func=lambda item: (
                f'{available[item]["name"]} · '
                f'{available[item]["type"]}'
            ),
            placeholder=t("geo.placeholder"),
            disabled=not enabled,
        )

        st.caption(
            t("geo.count", count=f"{len(features):,}")
        )

        return {
            "enabled": enabled,
            "categories": selected_categories,
            "labels": labels,
            "focus_id": selected_id,
            "i18n": {
                "latitude": t("geo.latitude"),
                "longitude": t("geo.longitude"),
                "centre": t("geo.real_centre"),
                "record": t("geo.record"),
            },
        }


class GeographicLayer(MacroElement):
    _template = Template(r"""
    {% macro script(this, kwargs) %}
    (function () {
        const map = {{ this._parent.get_name() }};
        const rows = {{ this.rows | safe }};
        const options = {{ this.options | safe }};
        const settings = {{ this.settings | safe }};
        const priorities = {{ this.priorities | safe }};

        const pinned = L.layerGroup().addTo(map);
        const labels = L.layerGroup().addTo(map);

        const cluster = L.markerClusterGroup({
            maxClusterRadius: settings.cluster_radius,
            disableClusteringAtZoom: settings.cluster_disable_zoom,
            chunkedLoading: true,
            animate: false,
            showCoverageOnHover: false
        }).addTo(map);

        const icon = L.divIcon({
            className: "",
            html: '<div style="width:12px;height:12px;'
                + 'background:#e98c59;border:2px solid white;'
                + 'border-radius:50%;box-sizing:border-box"></div>',
            iconSize: [12,12],
            iconAnchor: [6,6]
        });

        const cache = new Map();
        const active = new Map();
        let timer;

        function limit(rules, zoom) {
            let value = rules[0][1];
            for (const rule of rules) {
                if (zoom >= rule[0]) value = rule[1];
            }
            return value;
        }

        function minZoom(feature) {
            if (priorities[feature.id]) return 0;
            for (const rule of settings.size_rules) {
                if (feature.diameter_km >= rule[0]) {
                    return rule[1];
                }
            }
            return 8;
        }

        function priority(feature) {
            return (feature.id === options.focus_id ? 1000 : 0)
                + (priorities[feature.id] || 0);
        }

        function rank(a, b) {
            return priority(b) - priority(a)
                || b.diameter_km - a.diameter_km
                || Number(a.id) - Number(b.id);
        }

        function text(value) {
            const element = document.createElement("span");
            element.textContent = value;
            return element;
        }

        function popup(feature) {
            const box = document.createElement("div");
            const heading = document.createElement("strong");
            heading.textContent = feature.name;
            box.appendChild(heading);

            for (const value of [
                feature.type,
                options.i18n.latitude + feature.lat,
                options.i18n.longitude + feature.lon,
                options.i18n.centre
            ]) {
                const line = document.createElement("div");
                line.textContent = value;
                box.appendChild(line);
            }

            const link = document.createElement("a");
            link.href = "https://planetarynames.wr.usgs.gov/Feature/"
                + encodeURIComponent(feature.id);
            link.textContent = options.i18n.record;
            link.target = "_blank";
            link.rel = "noopener noreferrer";
            box.appendChild(link);
            return box;
        }

        function marker(feature) {
            if (!cache.has(feature.id)) {
                const item = L.marker(
                    [feature.lat, feature.lon],
                    {icon: icon, title: feature.name}
                );
                item.bindPopup(() => popup(feature));
                item.bindTooltip(() => text(feature.name));
                cache.set(feature.id, item);
            }
            return cache.get(feature.id);
        }

        function refreshLabels() {
            labels.clearLayers();
            if (!options.enabled || !options.labels) return;

            const zoom = Math.floor(map.getZoom());
            const budget = limit(settings.label_limits, zoom);
            const size = map.getSize();
            const occupied = [];
            let count = 0;

            const features = [...active.values()]
                .map(item => item.feature)
                .sort(rank);

            for (const feature of features) {
                if (count >= budget) break;

                const item = cache.get(feature.id);
                if (!map.hasLayer(item)) continue;

                if (!pinned.hasLayer(item)
                    && cluster.getVisibleParent(item) !== item) {
                    continue;
                }

                const point = map.latLngToContainerPoint(
                    [feature.lat, feature.lon]
                );

                const width = feature.name.length * 7 + 16;
                const box = {
                    left: point.x - width / 2,
                    right: point.x + width / 2,
                    top: point.y - 34,
                    bottom: point.y - 8
                };

                if (box.left < 4 || box.right > size.x - 4
                    || box.top < 4 || box.bottom > size.y - 4) {
                    continue;
                }

                const overlaps = occupied.some(other => !(
                    box.right + 8 < other.left
                    || box.left - 8 > other.right
                    || box.bottom + 8 < other.top
                    || box.top - 8 > other.bottom
                ));

                if (overlaps) continue;
                occupied.push(box);

                L.tooltip({
                    permanent: true,
                    direction: "top",
                    offset: [0,-8],
                    opacity: 0.95
                })
                .setLatLng([feature.lat, feature.lon])
                .setContent(text(feature.name))
                .addTo(labels);

                count += 1;
            }
        }

        function refresh() {
            const zoom = Math.floor(map.getZoom());
            const bounds = map.getBounds().pad(0.12);

            const selected = options.enabled
                ? rows.filter(feature =>
                    options.categories.includes(feature.category)
                    && bounds.contains([feature.lat, feature.lon])
                    && (
                        feature.id === options.focus_id
                        || zoom >= minZoom(feature)
                    )
                ).sort(rank).slice(
                    0, limit(settings.marker_limits, zoom)
                )
                : [];

            const wanted = new Set(
                selected.map(feature => feature.id)
            );

            for (const [id, item] of active) {
                if (!wanted.has(id)) {
                    pinned.removeLayer(item.marker);
                    cluster.removeLayer(item.marker);
                    active.delete(id);
                }
            }

            const additions = [];

            for (const feature of selected) {
                if (active.has(feature.id)) continue;

                const item = marker(feature);
                active.set(feature.id, {
                    feature: feature,
                    marker: item
                });

                if (priorities[feature.id]
                    || feature.id === options.focus_id) {
                    pinned.addLayer(item);
                } else {
                    additions.push(item);
                }
            }

            if (additions.length) cluster.addLayers(additions);
            refreshLabels();
        }

        const focus = rows.find(
            feature => feature.id === options.focus_id
        );

        if (focus && options.enabled) {
            map.setView(
                [focus.lat, focus.lon],
                settings.search_zoom,
                {animate: false}
            );
        }

        map.on("moveend zoomend", function () {
            clearTimeout(timer);
            timer = setTimeout(refresh, settings.debounce_ms);
        });

        cluster.on(
            "animationend spiderfied unspiderfied",
            refreshLabels
        );

        refresh();

        if (focus && active.has(focus.id)) {
            active.get(focus.id).marker.openPopup();
        }
    })();
    {% endmacro %}
    """)

    def __init__(self, options):
        super().__init__()
        self._name = "USGSMarsGeography"

        def encode(value):
            return json.dumps(
                value,
                ensure_ascii=False,
                separators=(",", ":"),
                allow_nan=False,
            ).replace("<", "\\u003c")

        self.rows = encode(load_catalogue())
        self.options = encode(options)
        self.settings = encode(DISPLAY)
        self.priorities = encode(PRIORITIES)


def add_geographic_features(mars_map, options):
    if options is None:
        return

    if mars_map.crs != "EPSG4326":
        raise ValueError(
            "Attach USGS geography only to the NASA angular "
            "global map, not to a CRS.Simple local map."
        )

    # Registers the Leaflet MarkerCluster JavaScript and CSS.
    MarkerCluster(
        name="USGS geographic features",
        control=False,
    ).add_to(mars_map)

    GeographicLayer(options).add_to(mars_map)


if __name__ == "__main__":
    result = download_catalogue()
    print(f"Saved {len(result)} official USGS Mars features.")
    print(f"JSON: {DATA_FILE}")
    print(f"Metadata: {META_FILE}")

