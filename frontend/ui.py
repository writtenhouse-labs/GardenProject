from pathlib import Path
import base64
from contextlib import contextmanager

import streamlit as st


ASSET_DIR = Path(__file__).parent / "assets"
GREEN = "#157a36"
GREEN_TRANSLUCENT = "rgba(21, 122, 54, 0.62)"
ORANGE = "rgb(238, 93, 27)"

PUBLIC_NAV_ITEMS = [
    ("Home", "/", "carrot.png"),
    ("Contact Us", "/Contact_Us", "onion.png"),
]

LOGGED_OUT_NAV_ITEMS = [
    ("Login", "/Login", "corn.png"),
    ("Register", "/Register", "capsicum.png"),
    ("Careers", "/Careers", "artichoke.png"),
]

LOGGED_IN_NAV_ITEMS = [
    ("Profile", "/Profile", "capsicum.png"),
    ("Logout", "/Logout", "corn.png"),
]

APPLICANT_NAV_ITEMS = [
    ("Careers", "/Careers", "artichoke.png"),
]


def icon_path(filename: str) -> str:
    return str(ASSET_DIR / filename)


def icon_data_uri(filename: str) -> str:
    data = (ASSET_DIR / filename).read_bytes()
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def configure_page(title: str, icon: str) -> None:
    st.set_page_config(page_title=f"{title} | Employee Portal", page_icon=icon_path(icon))
    inject_css()


def initialize_session() -> None:
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("user_email", "")
    st.session_state.setdefault("user_role", "")


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: #f8f9fa;
        }}
        .block-container {{
            max-width: 900px;
            padding-top: 2rem;
        }}
        section[data-testid="stSidebar"],
        div[data-testid="collapsedControl"] {{
            display: none;
        }}
        div[data-testid="stHorizontalBlock"] {{
            align-items: center;
        }}
        .garden-nav {{
            background-color: {GREEN_TRANSLUCENT};
            border-radius: 0;
            min-height: 128px;
            padding: 1.35rem 1rem;
            margin: 0 -1rem 2rem -1rem;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        .garden-nav a {{
            color: white;
            text-decoration: none;
            display: flex;
            flex-direction: column;
            align-items: center;
            font-size: 12px;
            line-height: 1;
            min-width: 64px;
            padding: 8px 10px;
            transition: 0.2s;
        }}
        .garden-nav a:hover {{
            color: white;
            transform: scale(1.1);
        }}
        .garden-nav img {{
            width: 42px;
            height: 42px;
            object-fit: contain;
            margin-bottom: 5px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 999px;
            padding: 4px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.18);
        }}
        section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: transparent;
            box-shadow: none;
            border: 0 !important;
            min-height: 0;
            max-width: none;
            margin: 0;
            display: block;
        }}
        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlockBorderWrapper"] > div {{
            padding: 0;
        }}
        div[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: white;
            border-radius: 6px;
            box-shadow: 0 .125rem .25rem rgba(0,0,0,.075);
            margin: 0 auto 2rem auto;
            max-width: 760px;
            min-height: 360px;
            display: flex;
            align-items: center;
            border: 0 !important;
        }}
        div[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"] > div {{
            width: 100%;
            padding: 2rem;
        }}
        div[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"] h1,
        div[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"] p,
        div[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"] strong,
        div[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"] label {{
            color: #212529;
        }}
        .portal-heading {{
            text-align: center;
            margin-bottom: 1.5rem;
        }}
        .portal-heading img {{
            width: 70px;
            height: 70px;
            object-fit: contain;
            margin-bottom: 1rem;
        }}
        .portal-heading h1 {{
            font-size: 1.75rem;
            margin-bottom: 0.25rem;
        }}
        .muted {{
            color: #6c757d;
        }}
        .footer-icons {{
            border-top: 1px solid #dee2e6;
            display: flex;
            justify-content: center;
            gap: 2rem;
            padding-top: 1rem;
            margin-top: 2rem;
            color: {GREEN_TRANSLUCENT};
        }}
        .footer-icons span {{
            display: flex;
            flex-direction: column;
            align-items: center;
            font-size: 0.8rem;
            transition: 0.2s;
        }}
        .footer-icons span:hover {{
            color: {ORANGE};
            transform: scale(1.1);
        }}
        .stButton > button {{
            background-color: #198754;
            color: white;
            border: 1px solid #198754;
            border-radius: 0.375rem;
            padding: 0.55rem 1rem;
            font-weight: 600;
        }}
        .stButton > button:hover {{
            background-color: #157347;
            color: white;
            border-color: #146c43;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_nav() -> None:
    initialize_session()
    nav_items = list(PUBLIC_NAV_ITEMS)
    if st.session_state["logged_in"]:
        nav_items.extend(LOGGED_IN_NAV_ITEMS)
        if st.session_state.get("user_role") == "applicant":
            nav_items.extend(APPLICANT_NAV_ITEMS)
    else:
        nav_items.extend(LOGGED_OUT_NAV_ITEMS)

    links = []
    for label, target, icon in nav_items:
        links.append(
            f'<a href="{target}" target="_self"><img src="{icon_data_uri(icon)}" alt="{label}"><span>{label}</span></a>'
        )
    st.markdown(f'<nav class="garden-nav">{"".join(links)}</nav>', unsafe_allow_html=True)


def render_heading(icon: str, title: str, subtitle: str = "") -> None:
    subtitle_html = f'<p class="muted">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div class="portal-heading">
            <img src="{icon_data_uri(icon)}" alt="{title}">
            <h1>{title}</h1>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


@contextmanager
def portal_card():
    with st.container(border=True):
        yield


def render_footer() -> None:
    st.markdown(
        """
        <div class="footer-icons">
            <span>✉<small>Subscribe</small></span>
            <span>↗<small>Share</small></span>
            <span>●<small>Alerts</small></span>
            <span>⚙<small>Settings</small></span>
        </div>
        """,
        unsafe_allow_html=True,
    )
