from pathlib import Path
import base64
from contextlib import contextmanager

import streamlit as st


ASSET_DIR = Path(__file__).parent / "assets"
GREEN = "#157a36"
GREEN_TRANSLUCENT = "#157a369c"
ORANGE = "rgb(238, 93, 27)"

PUBLIC_NAV_ITEMS = [
    ("Crop Intelligence", "/", "garlic.png"),
    ("Crop Progress", "/Crop_Progress", "broccoli.png"),
    ("Weather", "/Weather", "lemon.png"),
    ("Drought", "/Drought", "onion.png"),
    ("Yield History", "/Yield_History", "corn.png"),
    ("Similarity", "/Similarity", "avocado.png"),
]


def icon_path(filename: str) -> str:
    return str(ASSET_DIR / filename)


def icon_data_uri(filename: str) -> str:
    data = (ASSET_DIR / filename).read_bytes()
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def configure_page(title: str, icon: str) -> None:
    st.set_page_config(page_title=f"{title} | GardenProject", page_icon=icon_path(icon), layout="wide")
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
            --gp-page-max: 1180px;
            --gp-page-gutter: clamp(1rem, 2.5vw, 1.5rem);
            --gp-section-gap: 1rem;
            --gp-panel-padding: clamp(1.25rem, 2.4vw, 2rem);
            --gp-control-gap: 1rem;
            --gp-control-radius: 8px;
            --gp-panel-radius: 14px;
            --gp-border: #e2e8e4;
            --gp-page-bg: #f3f6f4;
            --gp-surface: #ffffff;
            --portal-shell-width: min(var(--gp-page-max), calc(100vw - (var(--gp-page-gutter) * 2)));
        }}
        .stApp {{
            background-color: var(--gp-page-bg);
        }}
        .block-container {{
            max-width: var(--gp-page-max);
            padding: 1.5rem var(--gp-page-gutter) 2rem;
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
        .intelligence-hero {{
            background:
                linear-gradient(90deg, rgba(238, 248, 234, .94) 0%, rgba(231, 246, 224, .82) 46%, rgba(228, 243, 218, .68) 100%),
                url("{icon_data_uri("field-hero.png")}") center 56% / cover no-repeat;
            border-radius: 18px;
            color: #173c25;
            padding: 3.4rem clamp(1.5rem, 5vw, 4rem);
            margin-bottom: var(--gp-section-gap);
            border: 1px solid rgba(185, 214, 175, .72);
            box-shadow: 0 10px 26px rgba(81, 128, 71, .10);
            position: relative;
            overflow: hidden;
        }}
        .intelligence-hero::after {{
            content: "◌"; position: absolute; right: 4%; top: -35%;
            font-size: 18rem; color: rgba(255,255,255,.08);
        }}
        .intelligence-hero h1 {{
            font-size: clamp(2rem, 4vw, 3.4rem); margin: .25rem 0 .75rem; max-width: 760px;
        }}
        .intelligence-hero p {{
            max-width: 780px; font-size: 1.05rem; line-height: 1.7;
            color: rgba(255,255,255,.86); margin: 0;
        }}
        .intelligence-hero::after {{
            content: "" !important;
            position: absolute;
            inset: 0;
            background: linear-gradient(180deg, rgba(255,255,255,.16), rgba(255,255,255,.38));
            pointer-events: none;
        }}
        .intelligence-hero h1,
        .intelligence-hero p,
        .intelligence-hero .eyebrow {{
            position: relative;
            z-index: 1;
        }}
        .intelligence-hero h1 {{
            color: #173c25;
        }}
        .intelligence-hero p {{
            color: #3e5d45;
        }}
        .intelligence-hero .eyebrow {{
            color: #5b8a4c;
        }}
        .eyebrow, .section-kicker, .optional-label, .results-heading span {{
            font-size: .72rem; font-weight: 800; letter-spacing: .14em;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker),
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-card-marker) {{
            background: var(--gp-surface); border: 1px solid var(--gp-border) !important; border-radius: var(--gp-panel-radius);
            box-shadow: 0 8px 24px rgba(26, 65, 39, .06);
            color: #1f2d24;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker) h1,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker) h2,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker) h3,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker) p,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker) label,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker) [data-testid="stWidgetLabel"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker) [data-testid="stWidgetLabel"] p {{
            color: #1f2d24;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker) > div {{
            padding: var(--gp-panel-padding);
            width: 100%;
            box-sizing: border-box;
            overflow: hidden;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker)
        > div > div[data-testid="stVerticalBlock"] {{
            width: auto !important;
            min-width: 0 !important;
            max-width: 100% !important;
            box-sizing: border-box;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-card-marker) > div {{ padding: 1.35rem; }}
        .intelligence-panel-marker, .result-card-marker {{ display:none; }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-card-marker) {{
            width: 100%;
            min-width: 0;
            max-width: 100%;
            box-sizing: border-box;
            overflow: hidden;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-card-marker) > div {{
            width: 100%;
            min-width: 0;
            max-width: 100%;
            box-sizing: border-box;
            overflow: hidden;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-card-marker)
        > div > div[data-testid="stVerticalBlock"] {{
            width: auto !important;
            min-width: 0 !important;
            max-width: 100% !important;
            box-sizing: border-box;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-card-marker)
        div[data-testid="stElementContainer"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-card-marker)
        div[data-testid="stMarkdown"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-card-marker)
        div[data-testid="stMarkdownContainer"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-card-marker)
        div[data-testid="stAlert"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-card-marker)
        div[data-testid="stExpander"] {{
            width: 100% !important;
            min-width: 0 !important;
            max-width: 100% !important;
            box-sizing: border-box;
        }}
        div[data-testid="stMainBlockContainer"] div[data-testid="stHorizontalBlock"]:has(.result-card-marker) {{
            width: 100%;
            max-width: 100%;
            gap: 1.25rem;
            align-items: stretch;
            box-sizing: border-box;
        }}
        div[data-testid="stMainBlockContainer"]
        div[data-testid="stHorizontalBlock"]:has(.result-card-marker)
        div[data-testid="column"] {{
            min-width: 0;
            max-width: 100%;
            box-sizing: border-box;
        }}
        .results-heading {{
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
        }}
        .section-heading {{
            display:flex; justify-content:space-between; align-items:end; gap:2rem;
            border-bottom:1px solid #e8eee9; padding-bottom:1rem; margin-bottom:var(--gp-control-gap);
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
        }}
        .section-heading h2, .results-heading h2 {{ margin:.15rem 0; font-size:1.45rem; }}
        .section-heading p {{ color:#68756c; max-width:470px; margin:0; }}
        .section-kicker, .results-heading span {{ color:{GREEN}; }}
        .optional-label {{ color:#718078; margin:1.4rem 0 .25rem; }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker)
        div[data-testid="stHorizontalBlock"] {{
            width: 100%;
            gap: var(--gp-control-gap);
            align-items: start;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker)
        div[data-testid="column"] {{
            min-width: 0;
            width: 100%;
            box-sizing: border-box;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker)
        div[data-testid="stElementContainer"] {{
            width: 100%;
            min-width: 0;
            max-width: 100%;
            box-sizing: border-box;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker)
        div[data-baseweb="select"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker)
        div[data-baseweb="input"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker)
        div[data-testid="stTextInputRootElement"],
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker)
        div[data-testid="stNumberInput"] {{
            width: 100%;
            min-width: 0;
            max-width: 100%;
            box-sizing: border-box;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker)
        div[data-baseweb="select"] > div,
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker)
        input {{
            box-sizing: border-box;
            max-width: 100%;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker)
        div[role="radiogroup"] {{
            width: auto !important;
            max-width: 100% !important;
            min-height: 40px;
            display: flex;
            align-items: center;
            gap: .8rem;
            flex-wrap: wrap;
            box-sizing: border-box;
        }}
        .field-note {{
            min-height: 66px;
            margin-top: 1.65rem;
            padding: .7rem .85rem;
            background: #fff8f3;
            border: 1px solid #f2ded1;
            border-radius: var(--gp-control-radius);
            box-sizing: border-box;
            color: #6a4a36;
            font-size: .78rem;
            line-height: 1.42;
        }}
        .field-note-neutral {{
            background: #f4f8f5;
            border-color: #dce8df;
            color: #506359;
        }}
        .assessment-button-marker {{ display: none; }}
        div[data-testid="stElementContainer"]:has(.assessment-button-marker)
        + div[data-testid="stElementContainer"] {{
            width: 50% !important;
            max-width: 50% !important;
            margin-left: auto;
            margin-right: auto;
        }}
        div[data-testid="stElementContainer"]:has(.assessment-button-marker)
        + div[data-testid="stElementContainer"] div[data-testid="stButton"],
        div[data-testid="stElementContainer"]:has(.assessment-button-marker)
        + div[data-testid="stElementContainer"] button {{
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box;
        }}
        .results-heading {{ margin:2.4rem 0 1rem; }}
        .card-title {{ display:flex; align-items:center; gap:.75rem; margin-bottom:1rem; }}
        .card-title,
        .card-title > div {{
            min-width: 0;
            max-width: 100%;
            box-sizing: border-box;
        }}
        .card-title small {{ color:#718078; font-weight:800; letter-spacing:.11em; }}
        .card-title h3 {{ margin:.05rem 0; font-size:1.15rem; }}
        .card-icon {{
            width:42px; height:42px; border-radius:12px; background:#edf7f0;
            display:flex; align-items:center; justify-content:center; font-size:1.25rem;
        }}
        .status-pill {{
            display:inline-block; border-radius:999px; padding:.25rem .65rem;
            font-size:.72rem; font-weight:800;
        }}
        .status-low, .status-on-track, .status-ahead {{ background:#dff3e5; color:#116530; }}
        .status-moderate {{ background:#fff1c7; color:#8a5a00; }}
        .status-high, .status-behind {{ background:#fde2df; color:#a52b20; }}
        .card-lead {{
            font-size:1.02rem;
            line-height:1.55;
            margin:.8rem 0 1.15rem;
            max-width: 100%;
            overflow-wrap: anywhere;
        }}
        .detail-grid {{
            display:grid;
            grid-template-columns:repeat(3,minmax(0, 1fr));
            gap:.65rem;
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
        }}
        .detail-grid div {{ background:#f5f8f6; border-radius:9px; padding:.75rem; }}
        .detail-grid span, .comparison-list span {{ display:block; color:#758079; font-size:.75rem; }}
        .detail-grid strong {{ display:block; font-size:.88rem; margin-top:.2rem; }}
        .comparison-list div {{
            display:flex; justify-content:space-between; gap:1rem;
            padding:.7rem 0; border-bottom:1px solid #edf0ee;
            min-width: 0;
            max-width: 100%;
            box-sizing: border-box;
        }}
        .comparison-list strong {{
            min-width: 0;
            font-size:.85rem;
            text-align:right;
            overflow-wrap: anywhere;
        }}
        .availability-note {{ font-size:.78rem; color:#7b847e; margin:.8rem 0 0; }}
        .risk-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            align-items: end;
            gap: 1rem;
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
        }}
        .risk-tile {{
            width: 100%;
            min-width: 0;
            border-radius: 11px;
            padding: 1rem;
            border-top: 4px solid;
            box-sizing: border-box;
            overflow-wrap: anywhere;
        }}
        .risk-low {{ background:#f2faf4; border-color:#36a15b; }}
        .risk-moderate {{ background:#fffaf0; border-color:#e1a824; }}
        .risk-high {{ background:#fff5f3; border-color:#d34b3f; }}
        .risk-tile h4 {{ margin:.85rem 0 .4rem; }}
        .risk-tile p {{
            color:#5e6962;
            font-size:.82rem;
            line-height:1.5;
            margin-bottom: 0;
        }}
        .season-row {{
            display:flex; justify-content:space-between; gap:.75rem; align-items:start;
            padding:.8rem 0; border-bottom:1px solid #edf0ee;
            width: 100%;
            min-width: 0;
            max-width: 100%;
            box-sizing: border-box;
        }}
        .season-row > div {{ min-width: 0; }}
        .season-row strong, .season-row span {{ display:block; }}
        .season-row span {{ color:#6d786f; font-size:.78rem; margin-top:.18rem; }}
        .season-row b {{ color:{GREEN}; white-space:nowrap; }}
        .agent-summary {{
            border-left:4px solid {ORANGE}; background:#fff8f3; margin:0;
            padding:1.15rem 1.25rem; border-radius:0 10px 10px 0;
            width: 100%;
            min-width: 0;
            max-width: 100%;
            box-sizing: border-box;
            overflow-wrap: anywhere;
            font-size:1.04rem; line-height:1.7; color:#333;
        }}
        .service-hero {{
            background: linear-gradient(135deg, #f0f8f2 0%, #ffffff 65%);
            border: 1px solid #dce9df;
            border-radius: 18px;
            padding: 2.4rem clamp(1.4rem, 4vw, 3rem);
            margin-bottom: 1.35rem;
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }}
        .service-hero img {{
            width: 92px;
            height: 92px;
            object-fit: contain;
            background: white;
            border-radius: 999px;
            padding: 10px;
            box-shadow: 0 8px 20px rgba(21, 122, 54, .12);
        }}
        .service-hero h1 {{
            margin: .15rem 0 .4rem;
            font-size: clamp(1.9rem, 4vw, 2.8rem);
            color: #183c25;
        }}
        .service-hero p {{
            margin: 0;
            max-width: 760px;
            color: #607067;
            line-height: 1.65;
        }}
        .service-card {{
            background: white;
            border: 1px solid #e0e8e2;
            border-radius: 15px;
            padding: clamp(1.3rem, 3vw, 2rem);
            box-shadow: 0 10px 28px rgba(24, 60, 37, .07);
        }}
        .service-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            gap: 1rem;
            padding-bottom: 1.1rem;
            border-bottom: 1px solid #e8eee9;
        }}
        .service-card-header h2 {{ margin: .15rem 0 0; font-size: 1.35rem; }}
        .source-link {{
            color: {GREEN};
            font-weight: 700;
            text-decoration: none;
        }}
        .source-link:hover {{ color: {ORANGE}; }}
        .service-data-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: .75rem;
            margin: 1.2rem 0;
        }}
        .service-data-item {{
            background: #f5f8f6;
            border-left: 3px solid #78ad87;
            border-radius: 8px;
            padding: .8rem .9rem;
            color: #34483b;
            font-size: .9rem;
        }}
        .service-note {{
            background: #fff8f3;
            border: 1px solid #f5dfd1;
            border-radius: 10px;
            padding: .9rem 1rem;
            color: #694a36;
            line-height: 1.55;
        }}
        @media (max-width: 800px) {{
            .section-heading {{
                display:block;
                width: 100%;
                max-width: 100%;
            }}
            .section-heading p {{ margin-top:.6rem; }}
            .detail-grid {{ grid-template-columns:1fr; }}
            .service-hero {{ align-items:flex-start; }}
            .service-hero img {{ width:68px; height:68px; }}
            .service-data-grid {{ grid-template-columns:1fr; }}
            .risk-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
            div[data-testid="stMainBlockContainer"]
            div[data-testid="stHorizontalBlock"]:has(.result-card-marker) {{
                flex-direction: column;
                gap: 1rem;
            }}
            div[data-testid="stMainBlockContainer"]
            div[data-testid="stHorizontalBlock"]:has(.result-card-marker)
            > div[data-testid="column"] {{
                width: 100% !important;
                flex: 1 1 100% !important;
            }}
            .garden-nav {{ min-height:100px; }}
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker) > div {{
                padding: var(--gp-panel-padding);
            }}
            div[data-testid="stVerticalBlockBorderWrapper"]:has(.intelligence-panel-marker)
            div[data-testid="stHorizontalBlock"] {{
                gap: .75rem;
            }}
            div[data-testid="stElementContainer"]:has(.assessment-button-marker)
            + div[data-testid="stElementContainer"] {{
                width: 100% !important;
                max-width: 100% !important;
            }}
        }}
        @media (max-width: 520px) {{
            .risk-grid {{ grid-template-columns: 1fr; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_nav() -> None:
    nav_items = list(PUBLIC_NAV_ITEMS)

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
