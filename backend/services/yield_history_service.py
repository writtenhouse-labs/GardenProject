from __future__ import annotations

from datetime import date
import os

import requests


REGIONAL_CROPS = {
    "AZ": ["Cotton", "Corn", "Wheat", "Barley", "Sorghum", "Alfalfa", "Lettuce"],
    "CA": ["Almonds", "Grapes", "Tomatoes", "Cotton", "Rice", "Wheat", "Corn"],
    "FL": ["Citrus", "Sugarcane", "Tomatoes", "Corn", "Peanuts"],
    "IA": ["Corn", "Soybeans", "Oats", "Hay"],
    "TX": ["Cotton", "Corn", "Wheat", "Sorghum", "Peanuts", "Rice"],
}
DEFAULT_CROPS = ["Corn", "Soybeans", "Wheat", "Cotton", "Sorghum", "Barley", "Hay"]


def available_crops(state_alpha: str, county_name: str | None = None) -> tuple[list[str], bool]:
    key = os.getenv("USDA_NASS_API_KEY", "")
    if not key:
        return REGIONAL_CROPS.get(state_alpha, DEFAULT_CROPS), True
    params = {
        "key": key,
        "sector_desc": "CROPS",
        "state_alpha": state_alpha,
        "year__GE": date.today().year - 5,
        "format": "JSON",
    }
    if county_name and "statewide" not in county_name.lower():
        params["county_name"] = county_name.upper().replace(" COUNTY", "")
        params["agg_level_desc"] = "COUNTY"
    try:
        response = requests.get(
            "https://quickstats.nass.usda.gov/api/api_GET/",
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        crops = sorted({row["commodity_desc"].title() for row in response.json().get("data", []) if row.get("commodity_desc")})
        return (crops[:40] or REGIONAL_CROPS.get(state_alpha, DEFAULT_CROPS)), not bool(crops)
    except (requests.RequestException, ValueError, KeyError):
        return REGIONAL_CROPS.get(state_alpha, DEFAULT_CROPS), True


def get_yield_history(crop: str, state_alpha: str, county_name: str | None) -> dict:
    key = os.getenv("USDA_NASS_API_KEY", "")
    if not key:
        return _fallback("USDA NASS API key is not configured")
    params = {
        "key": key,
        "commodity_desc": crop.upper(),
        "state_alpha": state_alpha,
        "statisticcat_desc": "YIELD",
        "year__GE": date.today().year - 10,
        "format": "JSON",
    }
    if county_name and "statewide" not in county_name.lower():
        params["county_name"] = county_name.upper().replace(" COUNTY", "")
    try:
        response = requests.get("https://quickstats.nass.usda.gov/api/api_GET/", params=params, timeout=15)
        if response.status_code == 400:
            try:
                detail = "; ".join(response.json().get("error", []))
            except (ValueError, TypeError):
                detail = "invalid query"
            return _fallback(
                f"USDA NASS rejected this crop/location yield query: {detail}. "
                "The selected commodity may not have a compatible county-level yield series."
            )
        response.raise_for_status()
        rows = response.json().get("data", [])
        values = []
        for row in rows:
            try:
                values.append({"year": int(row["year"]), "value": float(row["Value"].replace(",", "")), "unit": row["unit_desc"]})
            except (KeyError, TypeError, ValueError):
                continue
        values.sort(key=lambda item: item["year"], reverse=True)
        if not values:
            return _fallback("No matching USDA NASS yield records were returned")
        return {"records": values[:10], "source": "USDA NASS Quick Stats", "is_placeholder": False, "note": None}
    except requests.Timeout:
        return _fallback("USDA NASS timed out while retrieving yield history")
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        return _fallback(f"USDA NASS returned HTTP {status} while retrieving yield history")
    except (requests.RequestException, ValueError) as exc:
        return _fallback(f"USDA NASS unavailable: {type(exc).__name__}")


def _fallback(note: str) -> dict:
    return {
        "records": [],
        "source": "Yield history unavailable",
        "is_placeholder": True,
        "note": note,
    }
