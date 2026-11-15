"""Small HTML icons for markers (inline styles, no external CSS)."""
import folium


def stop_icon(label, color):
    """Round numbered badge for route stops."""
    html = (
        f'<div style="width:28px;height:28px;border-radius:50%;'
        f'background:{color};color:#fff;font:700 13px/24px sans-serif;'
        f'text-align:center;border:2px solid #fff;'
        f'box-shadow:0 0 8px rgba(0,0,0,.6)">{label}</div>'
    )
    return folium.DivIcon(
        html=html, icon_size=(28, 28), icon_anchor=(14, 14),
        class_name="mars-stop",
    )


def crosshair_icon():
    """Marker for the point selected by clicking the map."""
    html = (
        '<div style="width:24px;height:24px;border-radius:50%;'
        'border:2px solid #fff;box-shadow:0 0 8px rgba(0,0,0,.7);'
        'background:rgba(255,255,255,.12);position:relative">'
        '<div style="position:absolute;left:9px;top:9px;width:6px;'
        'height:6px;border-radius:50%;background:#fff"></div></div>'
    )
    return folium.DivIcon(
        html=html, icon_size=(24, 24), icon_anchor=(12, 12),
        class_name="mars-select",
    )
