from __future__ import annotations

from html import escape
import json

import requests
import streamlit as st

from api_client import get
from ui import configure_page, icon_data_uri, render_footer, render_nav


SERVICE_PAGES = {
    "crop_progress": {
        "title": "Crop Progress",
        "icon": "broccoli.png",
        "description": "Estimates the crop's current development stage and whether progress appears ahead, on track, or behind.",
        "source_name": "USDA Crop Progress & Condition Reports",
        "source_url": "https://www.nass.usda.gov/Charts_and_Maps/Crop_Progress_&_Condition/",
        "status": "Live API with fallback",
        "data": [
            "Estimated growth stage",
            "Weekly development change",
            "Progress status: ahead, on track, or behind",
            "Last-year and five-year progress comparisons",
            "Planting month or growing-season timing",
            "Crop and location context",
        ],
        "agent_use": "The agent uses these signals to explain whether crop development is proceeding normally and what stage-sensitive risks should be watched next.",
        "note": "Weekly state-level progress and condition estimates come from USDA NASS Quick Stats. The phenology model remains available for unsupported crop/state combinations; USDA web pages are not scraped.",
    },
    "weather": {
        "title": "Weather",
        "icon": "lemon.png",
        "description": "Collects recent climate observations used to evaluate heat exposure, rainfall, and temperature extremes.",
        "source_name": "NOAA Climate Data Online",
        "source_url": "https://www.ncei.noaa.gov/cdo-web/webservices/v2",
        "status": "Live API with fallback",
        "data": [
            "30-day average high temperature",
            "30-day average low temperature",
            "Accumulated precipitation",
            "Extreme-heat day count",
            "County-level observation coverage",
            "Weather-source availability",
        ],
        "agent_use": "The agent converts recent observations into heat-stress, rainfall-deficit, and temperature-extreme risk assessments.",
        "note": "A NOAA CDO token enables live observations. If NOAA is unavailable or no token is configured, the service returns a labeled demo weather baseline.",
    },
    "drought": {
        "title": "Drought",
        "icon": "onion.png",
        "description": "Evaluates current dryness and drought severity for the selected agricultural location.",
        "source_name": "U.S. Drought Monitor",
        "source_url": "https://droughtmonitor.unl.edu/",
        "status": "Live API with fallback",
        "data": [
            "Drought Severity and Coverage Index",
            "Current drought category",
            "Abnormally dry coverage",
            "Moderate through exceptional drought signals",
            "County FIPS location matching",
            "Recent drought reporting period",
        ],
        "agent_use": "The agent combines drought severity with rainfall and irrigation context to estimate crop water stress and near-term exposure.",
        "note": "The service uses the U.S. Drought Monitor REST data service. If it cannot be reached, a clearly labeled demo drought baseline keeps the assessment available.",
    },
    "yield_history": {
        "title": "Yield History",
        "icon": "corn.png",
        "description": "Retrieves historical crop production outcomes for comparison with current growing conditions.",
        "source_name": "USDA NASS Quick Stats",
        "source_url": "https://quickstats.nass.usda.gov/api",
        "status": "Live API with fallback",
        "data": [
            "Historical yield values",
            "Reporting year",
            "Yield unit",
            "Crop or commodity",
            "State and county geography",
            "Recent ten-year record window",
        ],
        "agent_use": "The agent uses available records to provide historical outcome context and support yield-risk interpretation.",
        "note": "A USDA NASS API key enables live records. When the API is unavailable, the agent reports that yield history is unavailable rather than inventing a comparison.",
    },
    "similarity": {
        "title": "Similarity",
        "icon": "avocado.png",
        "description": "Identifies past seasons with environmental and crop conditions resembling the current field profile.",
        "source_name": "Future vector database: pgvector, ChromaDB, or Pinecone",
        "source_url": "https://github.com/pgvector/pgvector",
        "status": "Placeholder model",
        "data": [
            "Crop and county",
            "Month and crop-development timing",
            "Rainfall and temperature",
            "Drought severity",
            "Historical yield",
            "Soil type and growing degree days",
        ],
        "agent_use": "The agent will use nearest-neighbor matches to explain similar years, similarity percentages, and the agricultural outcomes observed in those seasons.",
        "note": "Version 1 returns deterministic demo matches. The backend contains TODO integration points for pgvector and ChromaDB so the UI contract can remain stable.",
    },
}

RESULT_KEYS = {
    "crop_progress": "crop_progress",
    "weather": "weather",
    "drought": "drought",
    "yield_history": "yield_history",
    "similarity": "similarity",
}

IMPLEMENTED_SERVICE_NAMES = {
    "crop_progress": "Crop progress",
    "weather": "Weather",
    "drought": "Drought",
    "yield_history": "Yield history",
}


def render_service_page(service_key: str) -> None:
    service = SERVICE_PAGES[service_key]
    configure_page(service["title"], service["icon"])
    render_nav()

    live_status = None
    if service_key == "weather":
        try:
            live_status = get("/integrations/noaa/status")
        except requests.RequestException:
            live_status = {
                "configured": False,
                "message": "The GardenProject API is unavailable.",
            }

    st.markdown(
        f"""
        <section class="service-hero">
            <img src="{icon_data_uri(service["icon"])}" alt="{escape(service["title"])}">
            <div>
                <span class="section-kicker">CROP INTELLIGENCE SERVICE</span>
                <h1>{escape(service["title"])}</h1>
                <p>{escape(service["description"])}</p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    data_items = "".join(
        f'<div class="service-data-item">{escape(item)}</div>'
        for item in service["data"]
    )
    st.markdown(
        f"""
        <section class="service-card">
            <div class="service-card-header">
                <div>
                    <span class="section-kicker">INFORMATION CONTRACT</span>
                    <h2>Data supplied to the agent</h2>
                </div>
                <span class="status-pill status-moderate">{escape(service["status"])}</span>
            </div>
            <p><strong>Information source:</strong>
                <a class="source-link" href="{escape(service["source_url"])}" target="_blank">
                    {escape(service["source_name"])}
                </a>
            </p>
            <div class="service-data-grid">{data_items}</div>
            <p><strong>How the agent uses it:</strong> {escape(service["agent_use"])}</p>
            <div class="service-note"><strong>Availability and fallback:</strong> {escape(service["note"])}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    if live_status:
        if live_status["configured"]:
            st.success("NOAA integration configured. The token is stored server-side and is never sent to the browser.")
        else:
            st.error(
                f"{live_status['message']} Weather reports will default to demo data until NOAA_CDO_TOKEN is configured."
            )

    st.markdown(
        '<div class="results-heading"><span>LATEST AGENT RUN</span><h2>Raw integration results</h2></div>',
        unsafe_allow_html=True,
    )
    assessment = st.session_state.get("crop_assessment")
    if assessment is None:
        try:
            latest = get("/crop-intelligence/latest")
            assessment = latest.get("assessment") if latest.get("available") else None
        except requests.RequestException:
            assessment = None
        if assessment is not None:
            st.session_state["crop_assessment"] = assessment
    integration_results = assessment.get("integration_results", {}) if assessment else {}
    result = integration_results.get(RESULT_KEYS[service_key])

    if result is None:
        st.info(
            "No integration result is available yet. Run an assessment from Crop Intelligence, "
            "then return to this page."
        )
    else:
        _render_result_messages(service_key, result)
        st.code(json.dumps(result, indent=2, ensure_ascii=False), language="json")

    render_footer()


def _render_result_messages(service_key: str, result: dict) -> None:
    note = result.get("note")
    is_placeholder = bool(result.get("is_placeholder"))
    implemented_name = IMPLEMENTED_SERVICE_NAMES.get(service_key)

    if is_placeholder and implemented_name:
        st.error(
            f"The implemented {implemented_name} integration failed or was unavailable, "
            "so this result defaulted to demo data."
            f"{f' Provider message: {note}' if note else ''}"
        )
    elif is_placeholder:
        st.warning(
            "Demo data was used for this result."
            f"{f' Provider message: {note}' if note else ''}"
        )
    elif note:
        st.info(f"Provider message: {note}")
    else:
        st.success("Live or service-generated data was returned without a provider error.")

    if service_key == "yield_history" and not result.get("records"):
        st.error(
            note
            or "No historical yield records were returned for the selected crop and location."
        )
    elif service_key == "weather":
        missing = [
            label
            for key, label in (
                ("average_high_c", "average high temperature"),
                ("average_low_c", "average low temperature"),
                ("rainfall_mm", "precipitation"),
            )
            if result.get(key) is None
        ]
        if missing:
            st.error(
                "The implemented Weather integration returned incomplete data. "
                f"Missing NOAA fields: {', '.join(missing)}."
            )
    elif service_key == "drought" and result.get("dsci") is None:
        st.error("The drought response did not include a DSCI value.")
    elif service_key == "similarity" and not result.get("matches"):
        st.error("No similar-season matches were returned.")
