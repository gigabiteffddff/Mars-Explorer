"""Interface translations. To add a language: add it to LANGUAGES and add a
dict with the same keys to STRINGS (missing keys fall back to English).

Usage:  t("key", name=value)  ->  text in the language chosen in the sidebar.
        label("layer", "Radiation")  ->  translated name of a data item, or
        the item itself when no translation exists (e.g. USGS place names).
"""

LANGUAGES = {"en": "English", "uk": "Українська"}
DEFAULT_LANG = "en"
LANG_KEY = "lang"

STRINGS = {
    "en": {
        "language": "🌐 Language / Мова",
        "eyebrow": "EVA Mission Planner · Mars Surface Navigation",
        "planning": "Planning a terrain-aware route…",
        "download_route": "Download route — GeoJSON",
        "geo_unavailable": "Geographic features unavailable: {error}",
        "selected_point": "Selected point",

        "sb.map_layers": "Map layers",
        "sb.imagery": "NASA base imagery",
        "sb.basemap": "Base layer",
        "sb.hires": "Sharper Jezero imagery when zoomed in",
        "sb.opacity": "{name} opacity",
        "sb.contours": "Contour lines on data layers",
        "sb.markers": "Markers",
        "sb.sites": "Points of interest",
        "sb.labels": "Always show site names",
        "sb.hazards": "Simulated hazard zones",
        "sb.mission": "Mission planning",
        "sb.start": "Starting point",
        "sb.destinations": "Science destinations — selected order",
        "sb.mode": "Navigation mode",
        "sb.spacing": "Target grid spacing (m)",
        "sb.speed": "Travel speed (km/h)",
        "sb.use_selected": "Navigate to selected map point (last stop)",
        "sb.note": (
            "A* avoids simulated hazards and sampled slopes above 25°. "
            "Hazard avoidance applies even when zones are hidden. "
            "Up to 1000 km per leg, within ±80° latitude. "
            "Long routes use a coarser grid."
        ),

        "layer.Radiation": "Radiation",
        "layer.Temperature": "Temperature",
        "layer.Terrain": "Terrain",
        "basemap.Viking colour mosaic (232 m/px)":
            "Viking colour mosaic (232 m/px)",
        "basemap.MOLA colour shaded relief (463 m/px)":
            "MOLA colour shaded relief (463 m/px)",
        "mode.shortest": "Shortest",
        "mode.balanced": "Balanced",
        "mode.safe": "Safer terrain",
        "tag.DEMO": "DEMO",
        "tag.MOLA": "MOLA",
        "tag.model": "model",
        "unit.mGy/day": "mGy/day",
        "unit.°C": "°C",
        "unit.m": "m",
        "unit.mGy": "mGy",
        "unit.km": "km",
        "unit.min": "min",
        "unit.h": "h",
        "unit.d": "d",
        "unit.sols": "Martian sols",
        "site.Habitat Alpha": "Habitat Alpha",
        "site.Western delta": "Western delta",
        "site.Olympus Mons": "Olympus Mons",
        "site.Valles Marineris": "Valles Marineris",
        "site.Selected map point": "Selected map point",

        "panel.point": "Point",
        "panel.route": "Route",
        "panel.radiation": "Radiation",
        "panel.temperature": "Temperature",
        "panel.elevation": "Elevation",
        "panel.slope": "Slope",
        "panel.clear": "Clear selection",
        "panel.showing_start": (
            "Showing the starting point. Click anywhere on the "
            "map to inspect another location."
        ),
        "panel.distance": "Distance",
        "panel.travel_time": "Travel time",
        "panel.speed_line": "speed",
        "panel.leg": "Leg",
        "panel.km": "km",
        "panel.time": "Time",
        "panel.total": "Total",
        "panel.dose": "Radiation dose (model)",
        "panel.max_slope": "Maximum sampled slope",
        "panel.mode_line": "Mode: {mode} · grid ≈ {grid} m · {legs} leg(s)",
        "panel.route_note": (
            "Distance, time and dose follow the planned grid path. "
            "Maximum slope is sampled at nodes; terrain between "
            "nodes is unresolved. Safer mode penalizes terrain "
            "and dose rate; it does not guarantee a lower total dose."
        ),
        "panel.route_unavailable":
            "Route unavailable. Adjust the endpoints or grid spacing.",
        "panel.route_hint": (
            "Choose science destinations in the sidebar, "
            "or select a point on the map and enable navigation to it."
        ),
        "panel.objective_title": "Science objective",
        "panel.objective": (
            "Inspect geological textures and identify candidate sampling "
            "targets. Objectives and positions are illustrative."
        ),
        "panel.nasa_link": "NASA mission reference",

        "map.contours": "{name} contours — {tag}",
        "map.hazards": "Hazard zones — DEMO",
        "map.hazard_tip": "DEMO hazard — illustrative extent",
        "map.sites": "Points of interest",
        "map.route": "Navigation route",
        "map.route_tip": "A* route",
        "map.selected": "Selected point",
        "map.mars": "Mars",
        "map.lat_suffix": "°N",
        "map.lon_suffix": "°E",

        "err.legs_range": (
            "Legs must be within 1000 km and latitudes within ±80°. "
            "Add closer destinations."
        ),
        "err.in_hazard": "Start or destination is inside a hazard zone.",
        "err.grid_positive": "Grid spacing must be positive",
        "err.no_route": (
            "Leg {index}: no traversable route was found. "
            "Change the endpoints or use finer grid spacing. "
            "Possible causes: steep terrain, a hazard zone "
            "or insufficient search space for a detour."
        ),

        "geo.header": "Geographic Features",
        "geo.show_all": "Show all features",
        "geo.show_labels": "Show labels",
        "geo.search": "Search by name",
        "geo.placeholder": "Search an official Mars name…",
        "geo.count": "{count} official features · USGS/IAU",
        "geo.run_download":
            "Run `python mars_geo.py` once to download the USGS catalogue.",
        "geo.latitude": "Latitude: ",
        "geo.longitude": "Longitude: ",
        "geo.real_centre": "REAL catalogue centre · USGS/IAU",
        "geo.record": "Official USGS record",
        "category.Craters": "Craters",
        "category.Mountains": "Mountains",
        "category.Valleys": "Valleys",
        "category.Hills and Ridges": "Hills and Ridges",
        "category.Other features": "Other features",

        "footer.speed": "Travel speed is configured in the sidebar. ",
        "footer.routes": "Routes use A* on a sampled grid. ",
        "footer.imagery": (
            "Base imagery is real, georeferenced NASA Mars Trek imagery "
            "(Viking globally; CTX and HiRISE around Jezero). "
        ),
        "footer.dem": (
            "Elevation and slope are real MOLA topography (16 pixels/degree, "
            "~3.7 km, so slope is coarse). Radiation is a simplified model: "
            "galactic-cosmic-ray dose scaled from the atmospheric column "
            "depth that follows from elevation, calibrated on the dose "
            "Curiosity/RAD measured at Gale crater (0.21 mGy/day). It ignores "
            "solar particle events, seasons, dust and shielding. "
            "Temperature is synthetic."
        ),
        "footer.no_dem": (
            "The MOLA elevation file is missing (data/megt90n000eb.img), so "
            "elevation, slope and radiation are SYNTHETIC. Temperature is "
            "synthetic."
        ),
        "footer.tail": (
            " Jezero site positions are invented; the other landmarks use "
            "approximate real coordinates. Not for navigation or safety use."
        ),
        "footer.sources": "Data sources and future integration",
        "footer.future": (
            "Future versions can replace the radiation model with "
            "tables from a particle-transport code (HZETRN, "
            "GEANT4/PLANETOCOSMICS) and temperature with the Mars "
            "Climate Database. Solar radiation alerts are not "
            "implemented."
        ),
    },
    "uk": {
        "language": "🌐 Language / Мова",
        "eyebrow": "Планувальник місії EVA · Навігація поверхнею Марса",
        "planning": "Планування маршруту з урахуванням рельєфу…",
        "download_route": "Завантажити маршрут — GeoJSON",
        "geo_unavailable": "Географічні об'єкти недоступні: {error}",
        "selected_point": "Вибрана точка",

        "sb.map_layers": "Шари карти",
        "sb.imagery": "Базові знімки NASA",
        "sb.basemap": "Базовий шар",
        "sb.hires": "Чіткіші знімки Джезеро при наближенні",
        "sb.opacity": "Прозорість: {name}",
        "sb.contours": "Ізолінії на шарах даних",
        "sb.markers": "Маркери",
        "sb.sites": "Цікаві місця",
        "sb.labels": "Завжди показувати назви місць",
        "sb.hazards": "Змодельовані небезпечні зони",
        "sb.mission": "Планування місії",
        "sb.start": "Початкова точка",
        "sb.destinations": "Наукові цілі — у вибраному порядку",
        "sb.mode": "Режим навігації",
        "sb.spacing": "Цільовий крок сітки (м)",
        "sb.speed": "Швидкість руху (км/год)",
        "sb.use_selected": "Прокласти шлях до вибраної точки (остання зупинка)",
        "sb.note": (
            "A* оминає змодельовані небезпеки та ухили понад 25° у вибірці. "
            "Уникнення небезпек діє, навіть коли зони приховано. "
            "До 1000 км на відрізок, у межах широт ±80°. "
            "Довгі маршрути використовують грубішу сітку."
        ),

        "layer.Radiation": "Радіація",
        "layer.Temperature": "Температура",
        "layer.Terrain": "Рельєф",
        "basemap.Viking colour mosaic (232 m/px)":
            "Кольорова мозаїка Viking (232 м/піксель)",
        "basemap.MOLA colour shaded relief (463 m/px)":
            "Кольоровий рельєф MOLA з відмиванням (463 м/піксель)",
        "mode.shortest": "Найкоротший",
        "mode.balanced": "Збалансований",
        "mode.safe": "Безпечніший рельєф",
        "tag.DEMO": "ДЕМО",
        "tag.MOLA": "MOLA",
        "tag.model": "модель",
        "unit.mGy/day": "мГр/добу",
        "unit.°C": "°C",
        "unit.m": "м",
        "unit.mGy": "мГр",
        "unit.km": "км",
        "unit.min": "хв",
        "unit.h": "год",
        "unit.d": "д",
        "unit.sols": "марсіанських солів",
        "site.Habitat Alpha": "Оселя «Альфа»",
        "site.Western delta": "Західна дельта",
        "site.Olympus Mons": "Олімп (Olympus Mons)",
        "site.Valles Marineris": "Долини Марінера (Valles Marineris)",
        "site.Selected map point": "Вибрана точка на карті",

        "panel.point": "Точка",
        "panel.route": "Маршрут",
        "panel.radiation": "Радіація",
        "panel.temperature": "Температура",
        "panel.elevation": "Висота",
        "panel.slope": "Ухил",
        "panel.clear": "Скасувати вибір",
        "panel.showing_start": (
            "Показано початкову точку. Клацніть будь-де на карті, "
            "щоб переглянути іншу ділянку."
        ),
        "panel.distance": "Відстань",
        "panel.travel_time": "Час у дорозі",
        "panel.speed_line": "швидкість",
        "panel.leg": "Відрізок",
        "panel.km": "км",
        "panel.time": "Час",
        "panel.total": "Разом",
        "panel.dose": "Доза радіації (модель)",
        "panel.max_slope": "Максимальний ухил у вибірці",
        "panel.mode_line": (
            "Режим: {mode} · сітка ≈ {grid} м · відрізків: {legs}"
        ),
        "panel.route_note": (
            "Відстань, час і доза відповідають запланованому шляху по сітці. "
            "Максимальний ухил визначається у вузлах; рельєф між вузлами "
            "не розрізняється. Безпечніший режим штрафує рельєф і потужність "
            "дози, але не гарантує меншої сумарної дози."
        ),
        "panel.route_unavailable":
            "Маршрут недоступний. Змініть кінцеві точки або крок сітки.",
        "panel.route_hint": (
            "Оберіть наукові цілі на бічній панелі або виберіть точку "
            "на карті й увімкніть навігацію до неї."
        ),
        "panel.objective_title": "Наукова мета",
        "panel.objective": (
            "Дослідити геологічні текстури та визначити кандидатів для "
            "відбору зразків. Цілі й позиції є ілюстративними."
        ),
        "panel.nasa_link": "Сторінка місії на сайті NASA",

        "map.contours": "Ізолінії: {name} — {tag}",
        "map.hazards": "Небезпечні зони — ДЕМО",
        "map.hazard_tip": "ДЕМО-небезпека — ілюстративна межа",
        "map.sites": "Цікаві місця",
        "map.route": "Навігаційний маршрут",
        "map.route_tip": "Маршрут A*",
        "map.selected": "Вибрана точка",
        "map.mars": "Марс",
        "map.lat_suffix": "°пн.ш.",
        "map.lon_suffix": "°сх.д.",

        "err.legs_range": (
            "Відрізки мають бути до 1000 км, а широти — у межах ±80°. "
            "Додайте ближчі цілі."
        ),
        "err.in_hazard": "Початок або ціль лежить усередині небезпечної зони.",
        "err.grid_positive": "Крок сітки має бути додатним",
        "err.no_route": (
            "Відрізок {index}: прохідного маршруту не знайдено. "
            "Змініть кінцеві точки або зменште крок сітки. "
            "Можливі причини: крутий рельєф, небезпечна зона "
            "або замало простору для пошуку об'їзду."
        ),

        "geo.header": "Географічні об'єкти",
        "geo.show_all": "Показати всі об'єкти",
        "geo.show_labels": "Показувати підписи",
        "geo.search": "Пошук за назвою",
        "geo.placeholder": "Знайдіть офіційну назву на Марсі…",
        "geo.count": "{count} офіційних об'єктів · USGS/IAU",
        "geo.run_download": (
            "Один раз виконайте `python mars_geo.py`, щоб завантажити "
            "каталог USGS."
        ),
        "geo.latitude": "Широта: ",
        "geo.longitude": "Довгота: ",
        "geo.real_centre": "РЕАЛЬНИЙ центр з каталогу · USGS/IAU",
        "geo.record": "Офіційний запис USGS",
        "category.Craters": "Кратери",
        "category.Mountains": "Гори",
        "category.Valleys": "Долини",
        "category.Hills and Ridges": "Пагорби та хребти",
        "category.Other features": "Інші об'єкти",

        "footer.speed": "Швидкість руху налаштовується на бічній панелі. ",
        "footer.routes": "Маршрути будуються алгоритмом A* на сітці вибірки. ",
        "footer.imagery": (
            "Базові знімки — справжні георефіровані знімки NASA Mars "
            "Trek (Viking для всієї планети; CTX і HiRISE навколо Джезеро). "
        ),
        "footer.dem": (
            "Висота й ухил — справжня топографія MOLA (16 пікселів/градус, "
            "~3,7 км, тому ухил грубий). Радіація — спрощена модель: доза "
            "галактичних космічних променів, масштабована за товщею "
            "атмосфери, що випливає з висоти, і відкалібрована за дозою, "
            "виміряною Curiosity/RAD у кратері Гейл (0,21 мГр/добу). "
            "Модель не враховує сонячні спалахи, пори року, пил і екранування. "
            "Температура синтетична."
        ),
        "footer.no_dem": (
            "Файл висот MOLA відсутній (data/megt90n000eb.img), тому висота, "
            "ухил і радіація СИНТЕТИЧНІ. Температура синтетична."
        ),
        "footer.tail": (
            " Позиції місць у Джезеро вигадані; інші орієнтири мають "
            "приблизні справжні координати. Не для навігації чи безпеки."
        ),
        "footer.sources": "Джерела даних і майбутня інтеграція",
        "footer.future": (
            "У майбутніх версіях модель радіації можна замінити таблицями "
            "з коду транспорту частинок (HZETRN, GEANT4/PLANETOCOSMICS), "
            "а температуру — даними Mars Climate Database. Сповіщення про "
            "сонячну радіацію не реалізовані."
        ),
    },
}


def get_lang():
    """Language chosen in the sidebar; English outside of Streamlit."""
    try:
        import streamlit as st
        lang = st.session_state.get(LANG_KEY, DEFAULT_LANG)
    except Exception:  # noqa: BLE001
        return DEFAULT_LANG
    return lang if lang in STRINGS else DEFAULT_LANG


def translate(key, lang=None, **params):
    lang = lang or get_lang()
    text = STRINGS[lang].get(key)
    if text is None:
        text = STRINGS[DEFAULT_LANG].get(key, key)
    return text.format(**params) if params else text


def t(key, **params):
    return translate(key, None, **params)


def label(prefix, name):
    """Translated display name for an item, falling back to the item."""
    key = f"{prefix}.{name}"
    if key in STRINGS[DEFAULT_LANG]:
        return t(key)
    return str(name)


def render_language_switcher():
    """Call first in app.py so every later widget sees the chosen language."""
    import streamlit as st

    with st.sidebar:
        st.selectbox(
            t("language"),
            options=list(LANGUAGES),
            format_func=LANGUAGES.get,
            key=LANG_KEY,
        )


def site_label(name):
    return label("site", name)
