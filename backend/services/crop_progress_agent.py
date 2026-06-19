from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from services import crop_progress_service, drought_service, similarity_service, weather_service, yield_history_service
from services.location_service import counties, state_details, state_from_zipcode, states


def get_options(state_name: str | None = None, county_name: str | None = None, zipcode: str | None = None) -> dict:
    if zipcode and not state_name:
        state_name = state_from_zipcode(zipcode)
    if not state_name:
        return {
            "states": states(),
            "counties": [],
            "crops": yield_history_service.DEFAULT_CROPS if zipcode else [],
            "resolved_state": None,
            "placeholder": bool(zipcode),
            "note": "ZIP code lookup was unavailable; showing a national demo crop catalog." if zipcode else None,
        }
    state_alpha, _ = state_details(state_name)
    county_values, county_fallback = counties(state_name)
    crops, crop_fallback = yield_history_service.available_crops(state_alpha, county_name)
    return {
        "states": states(),
        "counties": county_values,
        "crops": crops,
        "resolved_state": state_name,
        "placeholder": county_fallback or crop_fallback,
        "note": "Crop choices use a regional demo catalog when USDA NASS is unavailable." if crop_fallback else None,
    }


def assess(request) -> dict:
    state_name = request.state or (state_from_zipcode(request.zipcode) if request.zipcode else "") or "United States"
    state_alpha, _ = state_details(state_name)
    location = f"{request.county}, {state_name}" if request.county else f"ZIP {request.zipcode}"
    with ThreadPoolExecutor(max_workers=4) as executor:
        progress_future = executor.submit(
            crop_progress_service.assess,
            request.crop,
            state_alpha,
            state_name,
            request.planting_month,
            request.growing_season,
        )
        weather_future = executor.submit(
            weather_service.get_weather, request.county_fips, request.zipcode
        )
        drought_future = executor.submit(drought_service.get_drought, request.county_fips)
        history_future = executor.submit(
            yield_history_service.get_yield_history,
            request.crop,
            state_alpha,
            request.county,
        )
        progress = progress_future.result()
        weather = weather_future.result()
        drought = drought_future.result()
        history = history_future.result()
    risks = _risks(weather, drought, request.irrigation)
    similar = similarity_service.find_similar_seasons({
        "crop": request.crop,
        "county": request.county or request.zipcode,
        "month": request.planting_month or request.growing_season,
        "rainfall": weather["rainfall_mm"],
        "temperature": weather["average_high_c"],
        "drought": drought["dsci"],
        "soil": request.soil_type,
    })
    elevated = [risk["name"].lower() for risk in risks if risk["level"] == "High"]
    caution = [risk["name"].lower() for risk in risks if risk["level"] == "Moderate"]
    concern = elevated[0] if elevated else caution[0] if caution else None
    summary = (
        f"{request.crop} in {location} appears to be {progress['progress_status'].lower()} "
        f"and is estimated at the {progress['estimated_growth_stage']} stage. "
    )
    summary += (
        f"The leading environmental concern is {concern}. "
        if concern
        else "Current environmental signals are generally favorable. "
    )
    if history["records"]:
        summary += "USDA yield history is available for comparison as conditions evolve."
    else:
        summary += "Yield history is currently unavailable, so the assessment uses weather, drought, and demo phenology signals."

    placeholders = [
        item["source"]
        for item in (progress, weather, drought, history, similar)
        if item.get("is_placeholder")
    ]
    return {
        "crop_status": {
            "crop": request.crop,
            "location": location,
            "estimated_growth_stage": progress["estimated_growth_stage"],
            "progress_status": progress["progress_status"],
            "statement": f"{request.crop} in {location} appears to be in the {progress['estimated_growth_stage']} stage.",
        },
        "progress_comparison": {
            "last_week": progress["last_week"],
            "last_year": progress["last_year"],
            "five_year_average": progress["five_year_average"],
            "unavailable_message": "Historical progress comparison data is not currently available.",
        },
        "risk_assessment": risks,
        "similar_seasons": similar,
        "agent_summary": summary,
        "yield_history": history,
        "integration_results": {
            "crop_progress": progress,
            "weather": weather,
            "drought": drought,
            "yield_history": history,
            "similarity": similar,
        },
        "data_quality": {
            "uses_placeholder_data": bool(placeholders),
            "placeholder_sources": placeholders,
            "sources": [progress["source"], weather["source"], drought["source"], history["source"], similar["source"]],
        },
    }


def _risks(weather: dict, drought: dict, irrigation: str | None) -> list[dict]:
    high = weather.get("average_high_c") or 0
    rainfall = weather.get("rainfall_mm")
    heat_level = "High" if high >= 35 or weather["extreme_heat_days"] >= 7 else "Moderate" if high >= 30 else "Low"
    drought_level = "High" if drought["dsci"] >= 200 else "Moderate" if drought["dsci"] >= 75 else "Low"
    rain_level = "Low" if rainfall is None else "High" if rainfall < 20 else "Moderate" if rainfall < 50 else "Low"
    extreme_level = "High" if weather["extreme_heat_days"] >= 10 else "Moderate" if weather["extreme_heat_days"] >= 3 else "Low"
    irrigation_note = " Irrigation can reduce immediate crop exposure." if irrigation == "Irrigated" else ""
    rainfall_explanation = (
        f"Approximately {rainfall} mm of precipitation was observed or estimated over the reporting period."
        if rainfall is not None
        else "NOAA precipitation observations were not available for the reporting period."
    )
    return [
        {"name": "Heat stress", "level": heat_level, "explanation": f"Recent average highs are about {high}°C; heat can raise crop water demand.{irrigation_note}"},
        {"name": "Drought conditions", "level": drought_level, "explanation": f"Current drought signal is {drought['category']} (DSCI {drought['dsci']})."},
        {"name": "Rainfall deficit", "level": rain_level, "explanation": rainfall_explanation},
        {"name": "Temperature extremes", "level": extreme_level, "explanation": f"{weather['extreme_heat_days']} recent days met the 35°C extreme-heat threshold."},
    ]
