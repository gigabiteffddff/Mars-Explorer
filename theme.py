import streamlit as st
import base64
from pathlib import Path

import streamlit as st


LOGO_PATH = (
    Path(__file__).resolve().parent
    / "assets"
    / "velvet-space-underground-lab.png"
)

CSS = """
<style>
:root {
    color-scheme: dark;
}

/* Space background */
.stApp {
    color: #e5edf8;
    background-color: #050d1b;
    background-image:
        radial-gradient(
            ellipse at 73% 0%, #24437b55, transparent 42%
        ),
        radial-gradient(
            ellipse at 26% 95%, #12356366, transparent 48%
        ),
        radial-gradient(
            1px 1px at 12% 16%, #b8dbff9c 90%, transparent
        ),
        radial-gradient(
            1px 1px at 64% 34%, #b8dbff80 90%, transparent
        ),
        radial-gradient(
            1px 1px at 88% 12%, #b8dbff90 90%, transparent
        );

    background-size:
        auto,
        auto,
        283px 247px,
        389px 317px,
        457px 281px;

    background-attachment: fixed;
}

/* Decorative planet */
.stApp::before {
    content: "";
    position: fixed;
    top: -195px;
    left: 65px;
    width: 370px;
    height: 370px;
    border-radius: 50%;
    pointer-events: none;

    background: radial-gradient(
        circle at 70% 70%,
        #05101e 24%,
        #543d40 62%,
        #bd7a61 78%,
        #edd0b6 84%,
        #27394e 86%
    );

    box-shadow: 12px 7px 60px #bf6f4226;
    opacity: .6;
}

/* Streamlit header: Deploy button hidden */
.stDeployButton,
[data-testid="stAppDeployButton"],
[data-testid="stToolbar"] .stAppDeployButton {
    display: none !important;
}

/* Streamlit header */
[data-testid="stHeader"] {
    background: #050d1b99;
    backdrop-filter: blur(12px);
}

[data-testid="stMainBlockContainer"] {
    max-width: 1800px;
    padding: 1.5rem 1.7rem 2rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(
        160deg, #0b1b30f5, #060f1ef5
    );
    border-right: 1px solid #25446199;
}

/* Фіксована ширина тільки для відкритої панелі */
[data-testid="stSidebar"][aria-expanded="true"] {
    width: 280px !important;
    min-width: 280px !important;
}

/* Кнопка повернення згорнутої панелі.
   Селектори для різних версій Streamlit. */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    top: 12px !important;
    left: 12px !important;
    z-index: 1000000 !important;
}

[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button {
    color: #eef3ff !important;
    background: #102038 !important;
    border: 1px solid #4b6888 !important;
    border-radius: 8px !important;
}

/* Декоративний напис не перехоплює натискання */
.mission-brand {
    pointer-events: none;
}

[data-testid="stSidebar"] h2 {
    font-size: .72rem;
    font-weight: 650;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: #d7e4f4;
    padding: .7rem 0 .4rem;
}

[data-testid="stSidebar"] label {
    font-size: .8rem;
}

[data-testid="stSidebar"] hr {
    border-color: #29425e;
    margin: 1.25rem 0;
}

/* Typography */
h1 {
    font-size: clamp(1.65rem, 2.6vw, 2.65rem) !important;
    font-weight: 650 !important;
    letter-spacing: -.025em;
    padding-bottom: .4rem !important;
}

h3 {
    font-size: .77rem !important;
    letter-spacing: .16em;
    text-transform: uppercase;
    color: #c7d8eb;
}

p, label, li {
    color: #cfdaea;
}

[data-testid="stCaptionContainer"] {
    color: #8fa6bf;
    font-size: .76rem;
    line-height: 1.6;
}

/* Inputs */
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stNumberInput"] [data-baseweb="input"] {
    background: #102038;
    border-color: #2b4868;
    border-radius: 8px;
}

/* Buttons */
.stButton button,
.stDownloadButton button,
.stLinkButton a {
    background: #0c1c31;
    color: #dceafa;
    border: 1px solid #4b6888;
    border-radius: 11px;
    font-size: .78rem;
    transition: border-color .15s, background .15s;
}

.stButton button:hover,
.stDownloadButton button:hover,
.stLinkButton a:hover {
    color: #71d5ff;
    border-color: #53bffa;
    background: #102d48;
}

button:focus-visible,
a:focus-visible {
    outline: 2px solid #63cfff !important;
    outline-offset: 3px;
}

/* Alerts */
[data-testid="stAlert"] {
    border: 1px solid #8e6a2c70;
    border-radius: 11px;
}

/* Metrics */
[data-testid="stMetricLabel"] p {
    color: #a9bbd0;
    font-size: .65rem;
    font-weight: 650;
    letter-spacing: .12em;
    text-transform: uppercase;
}

[data-testid="stMetricValue"] {
    color: #f0f5ff;
    font-size: 1.65rem;
    font-weight: 500;
}

[data-testid="stMetric"] {
    margin: .45rem 0 1rem;
}

/* Tabs */
[data-baseweb="tab-list"] {
    gap: 1.8rem;
    border-bottom: 1px solid #29425e;
}

[data-baseweb="tab"] {
    color: #9fb3cb;
    padding: .7rem .2rem;
}

[data-baseweb="tab"][aria-selected="true"] {
    color: #6bd5ff;
}

[data-baseweb="tab-highlight"] {
    background: #49c8ff;
}

/* Point / Route panel */
.st-key-mission-panel {
    background: linear-gradient(
        145deg, #0d2038ed, #071222ed
    );
    border: 1px solid #294b6e !important;
    border-radius: 14px !important;
    box-shadow: 0 14px 45px #00000025;
    padding: 1rem 1.2rem !important;
}

/* Map */
iframe[title="streamlit_folium.st_folium"] {
    border: 1px solid #365170;
    border-radius: 14px;
    background: #0b192a;
}

[data-testid="stExpander"] {
    background: #0b1b2c88;
    border-color: #29425e;
    border-radius: 10px;
}

/* Brand */
.mission-brand {
    position: fixed;
    top: 12px;
    left: 307px;
    right: 190px;
    z-index: 999990;
    height: 36px;
    display: flex;
    align-items: center;
    gap: 11px;
    color: #e0ebf8;
    font-size: .7rem;
    font-weight: 650;
    letter-spacing: .23em;
}

.mission-logo {
    position: relative;
    flex: 0 0 27px;
    width: 27px;
    height: 27px;
    border-radius: 50%;

    background: radial-gradient(
        circle at 30% 25%,
        #c7e8ff,
        #3977a9 28%,
        #0b1f35 72%
    );

    box-shadow: inset 0 0 0 1px #8cc9ee;
    margin-right: 5px;
}

.mission-logo::after {
    content: "";
    position: absolute;
    width: 39px;
    height: 11px;
    top: 8px;
    left: -6px;
    border: 1.5px solid #59bbef;
    border-radius: 50%;
    transform: rotate(-30deg);
}

.mission-status {
    margin-left: auto;
    font-size: .6rem;
    color: #8fb5d4;
    letter-spacing: .15em;
    border: 1px solid #294b6e;
    padding: 6px 10px;
    border-radius: 20px;
}

.mission-eyebrow {
    color: #9fb3cb;
    font-size: .65rem;
    letter-spacing: .2em;
    text-transform: uppercase;
    margin: -.3rem 0 1.1rem;
}

/* Mobile */
@media (max-width: 900px) {
    [data-testid="stMainBlockContainer"] {
        padding: 1.25rem 1rem;
    }

    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap;
    }

    [data-testid="stColumn"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 0 !important;
    }

    .mission-brand {
        left: 65px;
        right: 140px;
    }

    .mission-status {
        display: none;
    }
}
</style>

"""
BRAND_CSS = """
<style>
/* Remove the decorative planet */
.stApp::before {
    display: none;
}

.mission-brand {
    position: fixed;
    top: 9px;
    left: 307px;
    right: 190px;
    z-index: 999990;

    height: 44px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.mission-brand .brand-image {
    width: 44px;
    height: 44px;
    flex: 0 0 44px;
    object-fit: contain;
    border-radius: 7px;
}

.mission-brand .brand-name {
    color: #eef3ff;
    font-size: .7rem;
    font-weight: 650;
    letter-spacing: .11em;
    line-height: 1.3;
}

@media (max-width: 900px) {
    .mission-brand {
        left: 55px;
        right: 95px;
        gap: 8px;
    }

    .mission-brand .brand-image {
        width: 34px;
        height: 34px;
        flex-basis: 34px;
    }

    .mission-brand .brand-name {
        font-size: .58rem;
        letter-spacing: .06em;
    }

    .mission-status {
        display: none;
    }
}
</style>
"""

def apply_theme():
    st.html(CSS + BRAND_CSS)


def get_page_icon():
    return str(LOGO_PATH) if LOGO_PATH.is_file() else None


def render_brand():
    image_html = ""

    if LOGO_PATH.is_file():
        encoded = base64.b64encode(
            LOGO_PATH.read_bytes()
        ).decode("ascii")

        image_html = (
            '<img class="brand-image" '
            f'src="data:image/png;base64,{encoded}" '
            'alt="Velvet Space Underground Lab logo">'
        )

    st.html(
        '<div class="mission-brand">'
        f'{image_html}'
        '<span class="brand-name">'
        'VELVET SPACE UNDERGROUND LAB'
        '</span>'
        '</div>'
    )