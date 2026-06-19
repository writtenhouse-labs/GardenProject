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
        :root {{
            --portal-shell-width: min(900px, calc(100vw - 2rem));
        }}
        .stApp {{
            background-color: #f8f9fa;
        }}
        .block-container {{
            max-width: 900px;
            padding: 2rem 0;
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
            width: 100%;
            margin: 0 0 2rem 0;
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
            justify-content: center;
            align-items: center;
            flex: 0 0 84px;
            font-size: 12px;
            line-height: 1;
            padding: 8px 10px;
            box-sizing: border-box;
            text-align: center;
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
            margin: 0 auto 5px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 999px;
            padding: 4px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.18);
        }}
        .garden-nav span {{
            width: 100%;
            text-align: center;
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
        .portal-card-marker {{
            display: none;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) {{
            background: white;
            border-radius: 6px;
            box-shadow: 0 .125rem .25rem rgba(0,0,0,.075);
            margin: 0 0 2rem 0;
            max-width: none;
            width: 100%;
            min-height: 360px;
            display: flex;
            align-items: center;
            border: 0 !important;
            box-sizing: border-box;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) > div {{
            width: 100%;
            padding: 2rem;
            box-sizing: border-box;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) > div > div[data-testid="stVerticalBlock"] {{
            width: min(100%, 760px);
            max-width: 760px;
            margin: 0 auto;
            box-sizing: border-box;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stAlert"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stForm"] {{
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stElementContainer"] {{
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stMarkdown"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stMarkdownContainer"] {{
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
        }}
        div[data-testid="stMainBlockContainer"] div[data-testid="stForm"] {{
            width: 100%;
            box-sizing: border-box;
        }}
        div[data-testid="stMainBlockContainer"] div[data-testid="stForm"] > div {{
            width: 100%;
            box-sizing: border-box;
        }}
        div[data-testid="stMainBlockContainer"] div[data-testid="stTextInput"],
        div[data-testid="stMainBlockContainer"] div[data-testid="stTextInputRootElement"],
        div[data-testid="stMainBlockContainer"] div[data-testid="stNumberInput"],
        div[data-testid="stMainBlockContainer"] div[data-testid="stFileUploader"] {{
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
        }}
        div[data-testid="stMainBlockContainer"] input,
        div[data-testid="stMainBlockContainer"] textarea {{
            max-width: 100%;
            box-sizing: border-box;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)),
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) h1,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) p,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) strong,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) label {{
            color: #212529;
        }}
        .portal-heading {{
            text-align: center;
            margin-bottom: 1.5rem;
            width: 100%;
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
            text-align: center;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) h1,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) p {{
            text-align: center;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stMarkdownContainer"] {{
            text-align: center;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stForm"] label,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stForm"] label p,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stForm"] [data-testid="stWidgetLabel"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stForm"] [data-testid="stWidgetLabel"] p,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stTextInput"] label,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stTextInput"] label p,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stNumberInput"] label,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stNumberInput"] label p,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stFileUploader"] label,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stFileUploader"] label p,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[role="radiogroup"] {{
            text-align: left;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stAlert"] div[data-testid="stMarkdownContainer"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.portal-card-marker):not(:has(.garden-nav)) div[data-testid="stAlert"] p {{
            text-align: center;
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
        div[data-testid="stFormSubmitButton"] {{
            display: flex;
            justify-content: center;
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
        st.markdown('<span class="portal-card-marker"></span>', unsafe_allow_html=True)
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
