from __future__ import annotations

import calendar
from html import escape
import os

import requests
import streamlit as st

from api_client import get, post
from configuration import load_configuration
from field_map_component import render_field_map
from ui import configure_page, render_footer, render_nav


load_configuration()
configure_page("Crop Intelligence Agent", "garlic.png")
render_nav()

st.session_state.setdefault("field_location", {})

st.markdown(
    """
    <section class="intelligence-hero">
        <div class="eyebrow">AGRICULTURAL DECISION SUPPORT</div>
        <h1>Crop Intelligence Agent</h1>
        <p>Track crop development, evaluate environmental risks, compare historical growing conditions, and identify similar agricultural seasons.</p>
    </section>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=3600, show_spinner=False)
def load_base_options() -> dict:
    return get("/crop-intelligence/options")


@st.cache_data(ttl=1800, show_spinner=False)
def load_location_options(state: str = "", county: str = "", zipcode: str = "") -> dict:
    params = {"state": state, "county": county, "zipcode": zipcode}
    return get("/crop-intelligence/options", {key: value for key, value in params.items() if value})


def load_latest_assessment() -> dict | None:
    try:
        result = get("/crop-intelligence/latest")
    except requests.RequestException:
        return None
    return result.get("assessment") if result.get("available") else None


def pill(level: str) -> str:
    css_level = escape(level.lower().replace(" ", "-"))
    return f'<span class="status-pill status-{css_level}">{escape(level)}</span>'


def metric_value(value: str | None) -> str:
    return escape(value) if value else "Not currently available"


IMPLEMENTED_INTEGRATIONS = {
    "crop_progress": "Crop progress",
    "weather": "Weather",
    "drought": "Drought",
    "yield_history": "Yield history",
    "crop_rotation": "Crop rotation",
}
UNKNOWN_CROP_LABEL = "Unknown / identify from boundary"


def implemented_fallbacks(assessment: dict) -> list[str]:
    results = assessment.get("integration_results", {})
    failed = []
    for key, label in IMPLEMENTED_INTEGRATIONS.items():
        result = results.get(key, {})
        if result.get("is_placeholder"):
            note = result.get("note")
            failed.append(f"{label}: {note}" if note else label)
    return failed


try:
    base_options = load_base_options()
except requests.RequestException:
    base_options = {"states": [], "counties": [], "crops": []}
    st.error("The Crop Intelligence Agent API is not available. Start the GardenProject API and refresh this page.")

with st.container(border=True):
    st.markdown('<span class="intelligence-panel-marker"></span>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-heading">
            <div><span class="section-kicker">FIELD PROFILE</span><h2>Describe the crop and location</h2></div>
            <p>The agent combines live sources when available and clearly labels modeled or placeholder results.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    method_left, method_right = st.columns(2, gap="medium")
    with method_left:
        location_mode = st.radio("Location method", ["State and county", "ZIP code"], horizontal=True)
    with method_right:
        st.markdown(
            '<div class="field-note field-note-neutral"><strong>Location coverage</strong><br>Choose a county for the strongest geographic match, or use a five-digit ZIP code.</div>',
            unsafe_allow_html=True,
        )
    state = county = county_fips = zipcode = None
    map_center_query = ""

    if location_mode == "State and county":
        state_names = [item["name"] for item in base_options.get("states", [])]
        location_left, location_right = st.columns(2, gap="medium")
        with location_left:
            state = st.selectbox("State/Territory *", ["Select a state or territory"] + state_names)
        state_options = {"counties": [], "crops": []}
        if state != "Select a state or territory":
            try:
                state_options = load_location_options(state=state)
            except requests.RequestException:
                st.error("County options are temporarily unavailable.")
        county_lookup = {item["name"]: item for item in state_options.get("counties", [])}
        with location_right:
            county = st.selectbox("County *", ["Select a county"] + list(county_lookup))
        if state != "Select a state or territory" and county != "Select a county":
            map_center_query = f"{county}, {state}, USA"
        crop_options = state_options
        if county != "Select a county":
            county_details = county_lookup[county]
            county_fips = county_details["fips"]
            try:
                crop_options = load_location_options(state=state, county=county)
            except requests.RequestException:
                pass
    else:
        location_left, location_right = st.columns(2, gap="medium")
        with location_left:
            zipcode = st.text_input("ZIP code *", max_chars=5, placeholder="e.g., 85001")
        with location_right:
            st.text_input("Resolved state", value="", disabled=True, placeholder="Loaded from ZIP code")
        crop_options = {"crops": []}
        if len(zipcode) == 5 and zipcode.isdigit():
            map_center_query = f"{zipcode}, USA"
            try:
                crop_options = load_location_options(zipcode=zipcode)
                state = crop_options.get("resolved_state")
            except requests.RequestException:
                st.error("ZIP-based crop options are temporarily unavailable.")

    crops = crop_options.get("crops", [])
    crop_choices = [UNKNOWN_CROP_LABEL] + [item for item in crops if item != UNKNOWN_CROP_LABEL]
    crop_left, crop_right = st.columns(2, gap="medium")
    with crop_left:
        crop = st.selectbox("Crop", ["Select a crop"] + crop_choices, disabled=not crop_choices)
    with crop_right:
        if crop == UNKNOWN_CROP_LABEL:
            st.markdown(
                '<div class="field-note field-note-neutral"><strong>Crop identification mode</strong><br>The assessment will use field location, weather, drought, and rotation context while crop-specific progress waits for future CDL/CLU identification.</div>',
                unsafe_allow_html=True,
            )
        elif crop_options.get("note"):
            st.markdown(
                f'<div class="field-note"><strong>Demo data notice</strong><br>{escape(crop_options["note"])}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="field-note field-note-neutral"><strong>Data availability</strong><br>Live and fallback sources are evaluated when the assessment runs.</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="optional-label">FIELD LOCATION</div>', unsafe_allow_html=True)
    maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
    if map_center_query:
        if st.session_state.get("_field_map_context") != map_center_query:
            st.session_state["field_location"] = {}
            st.session_state["_field_map_context"] = map_center_query
        map_center = None
        if location_mode == "State and county" and county and county != "Select a county":
            county_details = county_lookup.get(county, {})
            if county_details.get("latitude") is not None and county_details.get("longitude") is not None:
                map_center = {
                    "latitude": county_details["latitude"],
                    "longitude": county_details["longitude"],
                }
        if maps_api_key:
            map_result = render_field_map(
                api_key=maps_api_key,
                center_query=map_center_query,
                center=map_center,
                value=st.session_state.get("field_location", {}),
            )
            if isinstance(map_result, dict):
                st.session_state["field_location"] = map_result
        else:
            st.info("GOOGLE_MAPS_API_KEY is not configured. Add it to the frontend service to enable field pin and boundary capture.")

        field_location = st.session_state.get("field_location", {})
        lat_value = field_location.get("latitude")
        lon_value = field_location.get("longitude")
        lat_col, lon_col, precision_col = st.columns(3, gap="medium")
        with lat_col:
            st.text_input("Latitude", value="" if lat_value is None else str(lat_value), disabled=True)
        with lon_col:
            st.text_input("Longitude", value="" if lon_value is None else str(lon_value), disabled=True)
        with precision_col:
            st.text_input("Location precision", value=field_location.get("precision", "regional"), disabled=True)
    else:
        st.markdown(
            '<div class="field-note field-note-neutral"><strong>Field map</strong><br>Select a county or enter a ZIP code to center the satellite map.</div>',
            unsafe_allow_html=True,
        )

    timing_left, timing_right = st.columns(2, gap="medium")
    with timing_left:
        timing_mode = st.radio("Crop timing *", ["Planting month", "Growing season"], horizontal=True)
    planting_month = growing_season = None
    with timing_right:
        if timing_mode == "Planting month":
            month_name = st.selectbox("Planting month", list(calendar.month_name)[1:])
            planting_month = list(calendar.month_name).index(month_name)
        else:
            growing_season = st.selectbox("Growing season", ["Cool season", "Warm season", "Year-round"])

    st.markdown('<div class="optional-label">OPTIONAL FIELD CONTEXT</div>', unsafe_allow_html=True)
    optional_row_one_left, optional_row_one_right = st.columns(2, gap="medium")
    with optional_row_one_left:
        irrigation = st.selectbox("Water source", ["Not specified", "Irrigated", "Rain-fed"])
    with optional_row_one_right:
        soil_type = st.selectbox(
            "Soil type",
            ["Not specified", "Sandy", "Sandy loam", "Loam", "Silt loam", "Clay loam", "Clay"],
        )
    optional_row_two_left, optional_row_two_right = st.columns(2, gap="medium")
    with optional_row_two_left:
        field_location = st.session_state.get("field_location", {})
        map_acres = field_location.get("acres")
        if map_acres and st.session_state.get("_map_acres_seen") != map_acres:
            st.session_state["field_size_input"] = float(map_acres)
            st.session_state["_map_acres_seen"] = map_acres
        field_size = st.number_input(
            "Field size (acres)",
            min_value=0.0,
            value=float(st.session_state.get("field_size_input", 0.0)),
            step=1.0,
            key="field_size_input",
        )
    with optional_row_two_right:
        objective = st.selectbox(
            "Objective",
            ["Monitor progress", "Estimate yield risk", "Compare historical seasons", "Recommend next steps"],
        )

    st.markdown('<span class="assessment-button-marker"></span>', unsafe_allow_html=True)
    run_assessment = st.button("Generate agricultural assessment", use_container_width=True, type="primary")

if run_assessment:
    valid_location = (
        location_mode == "State and county"
        and state
        and state != "Select a state or territory"
        and county
        and county != "Select a county"
    ) or (location_mode == "ZIP code" and zipcode and len(zipcode) == 5 and zipcode.isdigit())
    if not valid_location or crop == "Select a crop":
        st.info("Choose a valid location and select a crop or Unknown / identify from boundary before generating the assessment.")
    else:
        payload = {
            "latitude": st.session_state.get("field_location", {}).get("latitude"),
            "longitude": st.session_state.get("field_location", {}).get("longitude"),
            "location_precision": st.session_state.get("field_location", {}).get("precision"),
            "point_geojson": st.session_state.get("field_location", {}).get("point_geojson"),
            "field_boundary_geojson": st.session_state.get("field_location", {}).get("boundary_geojson"),
            "state": state,
            "county": county if county != "Select a county" else None,
            "county_fips": county_fips,
            "zipcode": zipcode,
            "crop": crop,
            "planting_month": planting_month,
            "growing_season": growing_season,
            "irrigation": None if irrigation == "Not specified" else irrigation,
            "soil_type": None if soil_type == "Not specified" else soil_type,
            "field_size": field_size or None,
            "objective": objective,
        }
        try:
            with st.spinner("Evaluating crop progress, weather, drought, and historical patterns..."):
                st.session_state["crop_assessment"] = post("/crop-intelligence/assess", payload)
        except requests.RequestException as exc:
            st.error(f"The assessment could not be completed: {exc}")

assessment = st.session_state.get("crop_assessment")
if assessment is None:
    assessment = load_latest_assessment()
    if assessment is not None:
        st.session_state["crop_assessment"] = assessment
if assessment:
    status = assessment["crop_status"]
    comparison = assessment["progress_comparison"]
    rotation = assessment.get("integration_results", {}).get("crop_rotation", {})
    st.markdown(
        '<div class="results-heading"><span>AGENT ASSESSMENT</span><h2>What the field signals suggest</h2></div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.05, 0.95])
    with left:
        with st.container(border=True):
            st.markdown('<span class="result-card-marker"></span>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="card-title"><span class="card-icon">🌱</span><div><small>DEVELOPMENT</small><h3>Crop Status</h3></div></div>
                <div>{pill(status["progress_status"])}</div>
                <p class="card-lead">{escape(status["statement"])}</p>
                <div class="detail-grid">
                    <div><span>Crop</span><strong>{escape(status["crop"])}</strong></div>
                    <div><span>Location</span><strong>{escape(status["location"])}</strong></div>
                    <div><span>Estimated stage</span><strong>{escape(status["estimated_growth_stage"].title())}</strong></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with right:
        with st.container(border=True):
            st.markdown('<span class="result-card-marker"></span>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="card-title"><span class="card-icon">📈</span><div><small>BENCHMARK</small><h3>Progress Comparison</h3></div></div>
                <div class="comparison-list">
                    <div><span>Last week</span><strong>{metric_value(comparison["last_week"])}</strong></div>
                    <div><span>Last year</span><strong>{metric_value(comparison["last_year"])}</strong></div>
                    <div><span>Five-year average</span><strong>{metric_value(comparison["five_year_average"])}</strong></div>
                </div>
                <p class="availability-note">{escape(comparison["unavailable_message"])}</p>
                """,
                unsafe_allow_html=True,
            )

    with st.container(border=True):
        st.markdown('<span class="result-card-marker"></span>', unsafe_allow_html=True)
        st.markdown(
            '<div class="card-title"><span class="card-icon">⚠️</span><div><small>EXPOSURE</small><h3>Environmental Risk Assessment</h3></div></div>',
            unsafe_allow_html=True,
        )
        risk_cards = "".join(
            f'<div class="risk-tile risk-{escape(risk["level"].lower())}">'
            f'<div>{pill(risk["level"])}</div>'
            f'<h4>{escape(risk["name"])}</h4>'
            f'<p>{escape(risk["explanation"])}</p>'
            f'</div>'
            for risk in assessment["risk_assessment"]
        )
        st.markdown(
            f'<div class="risk-grid">{risk_cards}</div>',
            unsafe_allow_html=True,
        )

    if rotation:
        sequence_rows = "".join(
            f"""
            <div class="season-row">
                <div><strong>{item["year"]}</strong><span>{escape(item["dominant_crop"])}</span></div>
                <b>{escape(str(item.get("planted_acres") or "demo"))}</b>
            </div>
            """
            for item in rotation.get("rotation_sequence", [])[:4]
        )
        with st.container(border=True):
            st.markdown('<span class="result-card-marker"></span>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="card-title"><span class="card-icon">R</span><div><small>ROTATION CONTEXT</small><h3>Historical Crop Rotation</h3></div></div>
                <div class="detail-grid">
                    <div><span>Previous crop</span><strong>{escape(str(rotation.get("previous_crop") or "Not available"))}</strong></div>
                    <div><span>Rotation diversity</span><strong>{escape(str(rotation.get("rotation_diversity_score", "Not available")))}</strong></div>
                    <div><span>Same crop run</span><strong>{escape(str(rotation.get("continuous_same_crop_years", "Not available")))} year(s)</strong></div>
                </div>
                <div class="rotation-sequence">{sequence_rows}</div>
                <p class="availability-note">{escape(rotation.get("note") or "")}</p>
                """,
                unsafe_allow_html=True,
            )

    similar_col, summary_col = st.columns([0.9, 1.1])
    with similar_col:
        with st.container(border=True):
            st.markdown('<span class="result-card-marker"></span>', unsafe_allow_html=True)
            st.markdown(
                '<div class="card-title"><span class="card-icon">🗓️</span><div><small>PATTERN MATCH</small><h3>Similar Seasons</h3></div></div>',
                unsafe_allow_html=True,
            )
            for match in assessment["similar_seasons"]["matches"]:
                st.markdown(
                    f"""
                    <div class="season-row">
                        <div><strong>{match["year"]}</strong><span>{escape(match["outcome"])}</span></div>
                        <b>{match["similarity_percent"]}%</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.caption("Demo similarity results; vector database integration is planned.")
    with summary_col:
        with st.container(border=True):
            st.markdown('<span class="result-card-marker"></span>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="card-title"><span class="card-icon">✨</span><div><small>PLAIN-ENGLISH OUTLOOK</small><h3>Agent Summary</h3></div></div>
                <blockquote class="agent-summary">{escape(assessment["agent_summary"])}</blockquote>
                """,
                unsafe_allow_html=True,
            )
            quality = assessment["data_quality"]
            failed_integrations = implemented_fallbacks(assessment)
            if failed_integrations:
                st.error(
                    "One or more implemented integrations failed or were unavailable, "
                    "so this report defaulted to demo data: "
                    + "; ".join(failed_integrations)
                )
            elif quality["uses_placeholder_data"]:
                st.warning(
                    "Demo data was used for clearly labeled sources: "
                    + ", ".join(quality.get("placeholder_sources", []))
                )
            with st.expander("Data sources and quality"):
                for source in quality["sources"]:
                    st.write(f"• {source}")

render_footer()
