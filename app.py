"""Entry point:  streamlit run app.py   (wiring only, no logic)."""
import folium
import streamlit as st
from streamlit_folium import st_folium

import map_layers as ml
from config import PAGE_TITLE
from geo import wrap_lon
from i18n import render_language_switcher, t
from icons import crosshair_icon
from panels import render_footer, render_info_panel
from navigation import RouteError, navigate, geojson_route
from sidebar import render_sidebar
from sites import SITES
from theme import apply_theme, render_brand, get_page_icon

try:  # USGS place-name layer is optional: the app must work without it
    from mars_geo import add_geographic_features, geographic_sidebar
except Exception:  # noqa: BLE001
    add_geographic_features = geographic_sidebar = None

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=get_page_icon(),
    layout="wide",
    initial_sidebar_state="expanded",
)

render_language_switcher()

apply_theme()
render_brand()

st.title(PAGE_TITLE)

st.html(
    f"""
    <div class="mission-eyebrow">
        {t("eyebrow")}
    </div>
    """
)

settings = render_sidebar()

geo_options = None
if geographic_sidebar is not None:
    try:
        geo_options = geographic_sidebar()
    except Exception as error:  # noqa: BLE001
        st.sidebar.warning(t("geo_unavailable", error=error))

route_names = [settings.start_name] + settings.destinations
route = [SITES[name] for name in route_names]
selected = st.session_state.get("selected_point")

if settings.use_selected and selected is not None:
    route_names.append("Selected map point")
    route.append(selected)


@st.cache_data(show_spinner=False, max_entries=32)
def cached_navigation(points, mode, spacing, speed):
    return navigate(
        points,
        mode=mode,
        resolution_m=spacing,
        speed_kmh=speed,
    )



stats = None
route_error = None

if len(route) > 1:
    try:
        with st.spinner(t("planning")):
            stats = cached_navigation(
                tuple(route),
                settings.route_mode,
                settings.resolution_m,
                settings.speed_kmh,
            )
    except RouteError as error:
        route_error = t(error.key, **error.params)
    except ValueError as error:
        route_error = str(error)

if route_error:
    st.error(route_error)

map_column, info_column = st.columns(
    [3.5, 1],
    gap="medium",
)
with info_column, st.container(
    border=True,
    key="mission-panel",
):
    render_info_panel(
        selected,
        settings,
        route_names,
        stats,
        route_error,
    )

    if stats:
        st.download_button(
            t("download_route"),
            data=geojson_route(stats),
            file_name="mars_route.geojson",
            mime="application/geo+json",
        )

with map_column:
    result = None
    m = ml.build_map()
    if settings.imagery:
        ml.add_imagery(m, settings.basemap, settings.hires)
    ml.add_data_layers(m, settings.controls, settings.contours)
    if settings.show_sites:
        ml.add_sites(m, settings.show_labels)
    if geo_options is not None:
        try:
            add_geographic_features(m, geo_options)
        except Exception as error:  # noqa: BLE001
            st.warning(t("geo_unavailable", error=error))
    ml.add_route(m,route_names,route,stats["coords"] if stats else [],)
    ml.add_controls(m)

    # selected point is passed separately so moving it needs no full redraw
    selection_group = folium.FeatureGroup(name=t("map.selected"))
    if selected:
        folium.Marker(selected, icon=crosshair_icon(),
                      tooltip=t("selected_point")).add_to(selection_group)

    result = st_folium(
        m, height=620, use_container_width=True,
        returned_objects=["last_clicked"],
        feature_group_to_add=selection_group, key="mars-map",
    )

clicked = (result or {}).get("last_clicked")

if clicked:
    new_point = (
        clicked["lat"],
        wrap_lon(clicked["lng"]),
    )

    if st.session_state.get("last_processed_map_click") != new_point:
        st.session_state["last_processed_map_click"] = new_point
        st.session_state["selected_point"] = new_point
        st.rerun()

render_footer()
