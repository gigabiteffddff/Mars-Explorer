"""Sidebar widgets. render_sidebar() returns a Settings object."""
from dataclasses import dataclass, field

import streamlit as st

from config import BASEMAPS, LAYERS
from fields import layer_tag
from i18n import label, site_label, t
from sites import SITES


@dataclass
class Settings:
    imagery: bool = True
    basemap: str = ""
    hires: bool = True
    controls: dict = field(default_factory=dict)  # name -> (on, opacity)
    contours: bool = True
    show_sites: bool = True
    show_labels: bool = True
    show_hazards: bool = True
    start_name: str = ""
    destinations: list = field(default_factory=list)
    route_mode: str = "balanced"
    resolution_m: int = 250
    speed_kmh: float = 3.0
    use_selected: bool = False


def render_sidebar():
    s = Settings()
    with st.sidebar:
        s.imagery = True
        s.basemap = "Viking colour mosaic (232 m/px)"
        s.hires = False

        for name, cfg in LAYERS.items():
            enabled = st.checkbox(
                label("layer", name), value=False, key=f"layer-{name}")
            opacity = 0.45
            if enabled:
                opacity = st.slider(
                    t("sb.opacity", name=label("layer", name)),
                    0.0, 1.0, 0.45, 0.05,
                    key=f"opacity-{name}",
                )
                st.markdown(
                    '<div style="height:10px;border-radius:4px;'
                    'background:linear-gradient(to right,'
                    f'{",".join(cfg["palette"])})"></div>',
                    unsafe_allow_html=True,
                )
                lo, hi = cfg["range"]
                st.caption(
                    f"{label('tag', layer_tag(name))} · "
                    f"{lo:g} → {hi:g} {label('unit', cfg['unit'])}")
            s.controls[name] = (enabled, opacity)
        contours: bool = True

        st.divider()
        st.header(t("sb.markers"))
        s.show_sites = st.checkbox(t("sb.sites"), True, key="show_sites")
        s.show_labels = st.checkbox(t("sb.labels"), True, key="show_labels")


        st.divider()
        st.header(t("sb.mission"))
        s.start_name = st.selectbox(
            t("sb.start"), list(SITES), key="start_name",
            format_func=site_label,
        )
        s.destinations = st.multiselect(
            t("sb.destinations"),
            [n for n in SITES if n != s.start_name],
            key="destinations",
            format_func=site_label,
        )
        s.route_mode = st.selectbox(
            t("sb.mode"),
            ["shortest", "balanced", "safe"],
            index=1,
            key="route_mode",
            format_func=lambda mode: label("mode", mode),
        )

        s.resolution_m = st.select_slider(
            t("sb.spacing"),
            options=[50, 100, 250, 500, 1000],
            value=250,
            key="resolution_m",
        )

        s.speed_kmh = st.number_input(
            t("sb.speed"),
            min_value=0.1,
            max_value=30.0,
            value=3.0,
            step=0.5,
            key="speed_kmh",
        )

        if st.session_state.get("selected_point") is not None:
            s.use_selected = st.checkbox(
                t("sb.use_selected"), key="use_selected"
            )

        st.caption(t("sb.note"))
    return s