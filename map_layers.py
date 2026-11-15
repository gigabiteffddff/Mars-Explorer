"""Functions that add things to a folium map. One function = one layer."""
import json

from navigation import geojson_route
import branca.colormap as cm
import folium
from branca.element import MacroElement, Template
from folium.plugins import Fullscreen, MousePosition, PolyLineTextPath

from config import (
    BASEMAPS, CONTOUR_OPACITY, CONTOUR_WEIGHT, HAZARD_COLOR, HIRES_LAYERS,
    LAYERS, ROUTE_COLOR, START_COLOR, START_VIEW, STOP_COLOR, TREK_URL,
)
from contours import contour_geojson
from fields import layer_tag
from geo import circle_points
from i18n import label, site_label, t
from icons import stop_icon
from rasters import overlay_images
from sites import DEFAULT_SITES, HAZARDS

WORLD = [[-90, -180], [90, 180]]  # south-west, north-east corner


class HideLeafletPrefix(MacroElement):
    """Removes the "Leaflet" credit; tile credits (NASA) stay visible."""

    _template = Template(
        """
        {% macro script(this, kwargs) %}
        (function () {
            const map = {{ this._parent.get_name() }};
            if (map.attributionControl) {
                map.attributionControl.setPrefix(false);
            }
        })();
        {% endmacro %}
        """
    )


def build_map():
    m = folium.Map(
        location=START_VIEW[:2],
        crs="EPSG4326",  # plain lat/lon grid, matches Trek's tile layout
        tiles=None,
        zoom_start=START_VIEW[2],
        min_zoom=1,
        max_zoom=18,
        zoom_snap=0.5,
        maxBounds=WORLD,
        maxBoundsViscosity=1.0,
    )
    HideLeafletPrefix().add_to(m)
    return m


def add_imagery(m, basemap_name, hires):
    layer_id, native = BASEMAPS[basemap_name]
    folium.TileLayer(
        tiles=TREK_URL.format(layer=layer_id, ext="jpg"),
        attr="NASA/JPL-Caltech · Mars Trek",
        name=basemap_name,
        min_zoom=0, max_zoom=18, max_native_zoom=native,
        no_wrap=True, overlay=False, control=False,
    ).add_to(m)

    if not hires:
        return
    for layer_name, layer_id, ext, first_zoom, deepest, cover in HIRES_LAYERS:
        folium.TileLayer(
            tiles=TREK_URL.format(layer=layer_id, ext=ext),
            attr="NASA/JPL-Caltech/USGS · Mars Trek",
            name=layer_name,
            min_zoom=first_zoom, max_zoom=18, max_native_zoom=deepest,
            bounds=cover, overlay=True, control=False,
        ).add_to(m)


def add_contours(m, name):
    """Dark smooth iso-lines of one data layer, in that layer's own colour."""
    cfg = LAYERS[name]
    data = contour_geojson(name)
    if not data["features"]:
        return  # nothing to draw; folium's tooltip crashes on empty data
    style = {
        "color": cfg["contour_color"],
        "weight": CONTOUR_WEIGHT,
        "opacity": CONTOUR_OPACITY,
    }
    folium.GeoJson(
        data,
        name=t("map.contours", name=label("layer", name),
               tag=label("tag", layer_tag(name))),
        style_function=lambda _feature, style=style: style,
        smooth_factor=0.5,
        tooltip=folium.GeoJsonTooltip(
            fields=["level"],
            aliases=[f"{label('layer', name)} "
                     f"({label('unit', cfg['unit'])})"],
            sticky=False,
        ),
    ).add_to(m)


def add_data_layers(m, controls, contours=True):
    """controls: {layer name: (enabled, opacity)}"""
    active = [n for n, (on, _) in controls.items() if on]
    if not active:
        return  # skip the (cached) raster work entirely
    images = overlay_images()
    for name in active:
        opacity = controls[name][1]
        folium.raster_layers.ImageOverlay(
            image=images[name], bounds=WORLD, origin="upper",
            opacity=opacity,
            name=f"{label('layer', name)} — "
                 f"{label('tag', layer_tag(name))}",
            interactive=False,
        ).add_to(m)
        if contours:
            add_contours(m, name)

    cfg = LAYERS[active[-1]]
    cm.LinearColormap(
        cfg["palette"], vmin=cfg["range"][0], vmax=cfg["range"][1],
        caption=(f"{label('tag', layer_tag(active[-1]))} · "
                 f"{label('layer', active[-1])} "
                 f"({label('unit', cfg['unit'])})"),
    ).add_to(m)


def add_hazards(m):
    group = folium.FeatureGroup(name=t("map.hazards"))
    for lat, lon, radius_km in HAZARDS:
        folium.Polygon(
            locations=circle_points(lat, lon, radius_km),
            color=HAZARD_COLOR, weight=2, dash_array="4 6",
            fill=True, fill_opacity=0.15,
            tooltip=t("map.hazard_tip"),
        ).add_to(group)
    group.add_to(m)


def add_sites(m, show_labels):
    group = folium.FeatureGroup(name=t("map.sites"))
    # only the curated points; the full USGS catalogue is drawn (clustered)
    # by mars_geo, 2000 permanent labels here would freeze the browser
    for site, (lat, lon) in DEFAULT_SITES.items():
        name = label("site", site)
        tooltip = (
            folium.Tooltip(name, permanent=True, direction="top",
                           offset=(0, -6))
            if show_labels else name
        )
        folium.CircleMarker(
            location=(lat, lon), radius=8, color="white",
            fill=True, fill_color=STOP_COLOR, fill_opacity=1,
            tooltip=tooltip,
            popup=folium.Popup(
                f"<b>{name}</b><br>{lat:.4f}°, {lon:.4f}°", max_width=200),
        ).add_to(group)
    group.add_to(m)


def add_route(m, route_names, route, path=None):
    group = folium.FeatureGroup(name=t("map.route"))

    if path and len(path) > 1:
        geometry = json.loads(
            geojson_route({"coords": path})
        )["geometry"]

        for segment in geometry["coordinates"]:
            line = folium.PolyLine(
                [(lat, lon) for lon, lat in segment],
                color=ROUTE_COLOR,
                weight=4,
                tooltip=t("map.route_tip"),
            ).add_to(group)

            PolyLineTextPath(
                line,
                "►",
                repeat=True,
                offset=7,
                attributes={
                    "fill": ROUTE_COLOR,
                    "font-size": "16",
                },
            ).add_to(group)

    for index, (name, point) in enumerate(
        zip(route_names, route)
    ):
        badge = "S" if index == 0 else str(index)

        folium.Marker(
            point,
            icon=stop_icon(
                badge,
                START_COLOR if index == 0 else STOP_COLOR,
            ),
            tooltip=f"{badge} · {site_label(name)}",
        ).add_to(group)

    group.add_to(m)


def add_controls(m):
    Fullscreen(position="topleft").add_to(m)
    MousePosition(
        position="bottomleft", separator=" | ", prefix=t("map.mars"),
        num_digits=4,
        lat_formatter=("function(n){return n.toFixed(4) + '"
                       + t("map.lat_suffix") + "';}"),
        lng_formatter=("function(n){return n.toFixed(4) + '"
                       + t("map.lon_suffix") + "';}"),
    ).add_to(m)
    folium.LayerControl(collapsed=True).add_to(m)