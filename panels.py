"""Right-hand info panel and footer text."""
import streamlit as st

from travel_time import format_duration, sols

from fields import dem_loaded, sample
from i18n import label, site_label, t
from sites import SITES


def render_info_panel(selected, settings, route_names, stats, route_error=None):
    tab_point, tab_route = st.tabs([t("panel.point"), t("panel.route")])

    with tab_point:
        lat, lon = selected or SITES[settings.start_name]
        values = sample(lat, lon)
        st.caption(f"LAT: {lat:.4f}° · LON: {lon:.4f}°")
        real = dem_loaded()

        st.metric(
            t("panel.radiation"),
            f'{float(values["radiation"]):.3f} {t("unit.mGy/day")}',
        )

        st.metric(
            t("panel.temperature"),
            f'{float(values["temperature"]):.1f} {t("unit.°C")}',
        )

        st.metric(
            t("panel.elevation"),
            f'{float(values["elevation"]):.0f} {t("unit.m")}',
        )

        st.metric(
            t("panel.slope"),
            f'{float(values["slope"]):.1f}°',
        )
        if selected:
            if st.button(t("panel.clear")):
                del st.session_state["selected_point"]
                st.rerun()
        else:
            st.caption(t("panel.showing_start"))

    with tab_route:
        if stats:
            names = [site_label(n) for n in route_names]
            st.caption(" → ".join(names))

            st.metric(
                t("panel.distance"),
                f'{stats["distance_km"]:.2f} {t("unit.km")}',
            )

            st.metric(
                t("panel.travel_time"),
                format_duration(stats["minutes"]),
            )

            st.caption(
                f'≈ {stats["minutes"]:.0f} {t("unit.min")} · '
                f'{sols(stats["minutes"]):.2f} {t("unit.sols")} · '
                f'{t("panel.speed_line")} {stats["speed_kmh"]:g} '
                f'{t("unit.km")}/{t("unit.h")}'
            )

            if len(stats["leg_details"]) > 1:
                rows = []
                elapsed = 0.0
                for i, leg in enumerate(stats["leg_details"]):
                    elapsed += leg["minutes"]
                    rows.append(
                        {
                            t("panel.leg"): f"{names[i]} → {names[i + 1]}",
                            t("panel.km"): round(leg["distance_km"], 2),
                            t("panel.time"): format_duration(leg["minutes"]),
                            t("panel.total"): format_duration(elapsed),
                        }
                    )
                st.dataframe(rows, hide_index=True, use_container_width=True)

            st.metric(
                t("panel.dose"),
                f'{stats["dose_mgy"]:.4f} {t("unit.mGy")}',
            )

            st.metric(
                t("panel.max_slope"),
                f'{stats["max_slope_deg"]:.1f}°',
            )

            st.caption(
                t(
                    "panel.mode_line",
                    mode=label("mode", stats["mode"]),
                    grid=f'{stats["grid_m"]:.0f}',
                    legs=stats["legs"],
                )
            )

            st.caption(t("panel.route_note"))

        elif route_error:
            st.warning(t("panel.route_unavailable"))

        else:
            st.info(t("panel.route_hint"))

    st.divider()
    st.subheader(t("panel.objective_title"))
    st.write(t("panel.objective"))
    st.link_button(
        t("panel.nasa_link"),
        "https://science.nasa.gov/mission/mars-2020-perseverance/"
        "location-map/",
    )


def render_footer():
    source = t("footer.dem") if dem_loaded() else t("footer.no_dem")
    st.caption(
        t("footer.speed")
        + t("footer.routes")
        + t("footer.imagery")
        + source
        + t("footer.tail")
    )
    with st.expander(t("footer.sources")):
        st.markdown(
            "- [NASA Mars Trek](https://trek.nasa.gov/mars/)\n"
            "- [MOLA MEGDR topography (PDS)]"
            "(https://pds-geosciences.wustl.edu/missions/mgs/megdr.html)\n"
            "- [USGS planetary names](https://planetarynames.wr.usgs.gov/)\n"
            "- [Planetary Data System](https://pds.nasa.gov/)\n"
            "- [Mars Orbital Data Explorer](https://ode.rsl.wustl.edu/mars/)"
        )
        st.write(t("footer.future"))
