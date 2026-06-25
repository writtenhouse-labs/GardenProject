from __future__ import annotations

from collections import defaultdict
from datetime import date
import os

import requests

from services.yield_history_service import DEFAULT_CROPS, REGIONAL_CROPS


QUICK_STATS_URL = "https://quickstats.nass.usda.gov/api/api_GET/"
REQUEST_TIMEOUT = 15
LOOKBACK_YEARS = 8


def get_crop_rotation(crop: str, state_alpha: str, county_name: str | None) -> dict:
    # TODO: Add USDA Cropland Data Layer/CDL sampling by lat/lon or field boundary.
    key = os.getenv("USDA_NASS_API_KEY", "").strip()
    if not key:
        return _fallback(crop, state_alpha, "USDA NASS API key is not configured")
    if not state_alpha:
        return _fallback(crop, state_alpha, "State information is unavailable for the USDA query")

    params = {
        "key": key,
        "sector_desc": "CROPS",
        "state_alpha": state_alpha,
        "statisticcat_desc": "AREA PLANTED",
        "year__GE": date.today().year - LOOKBACK_YEARS,
        "format": "JSON",
    }
    if county_name and "statewide" not in county_name.lower():
        params["county_name"] = county_name.upper().replace(" COUNTY", "")
        params["agg_level_desc"] = "COUNTY"
    else:
        params["agg_level_desc"] = "STATE"

    try:
        response = requests.get(QUICK_STATS_URL, params=params, timeout=REQUEST_TIMEOUT)
        if response.status_code == 400:
            try:
                detail = "; ".join(response.json().get("error", []))
            except (ValueError, TypeError):
                detail = "invalid query"
            return _fallback(crop, state_alpha, f"USDA NASS rejected the crop rotation query: {detail}")
        response.raise_for_status()
        rows = response.json().get("data", [])
        return _summarize(rows)
    except requests.Timeout:
        return _fallback(crop, state_alpha, "USDA NASS timed out while retrieving crop rotation context")
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        return _fallback(crop, state_alpha, f"USDA NASS returned HTTP {status} while retrieving crop rotation context")
    except (requests.RequestException, ValueError) as exc:
        return _fallback(crop, state_alpha, f"USDA NASS unavailable: {type(exc).__name__}")


def _summarize(rows: list[dict]) -> dict:
    by_year: dict[int, list[dict]] = defaultdict(list)
    raw_records = []
    for row in rows:
        acres = _number(row.get("Value"))
        try:
            year = int(row["year"])
        except (KeyError, TypeError, ValueError):
            continue
        commodity = str(row.get("commodity_desc") or "").title()
        if not commodity or acres is None:
            continue
        record = {
            "year": year,
            "crop": commodity,
            "planted_acres": acres,
            "unit": row.get("unit_desc") or "ACRES",
            "state": row.get("state_alpha"),
            "county": row.get("county_name"),
        }
        raw_records.append(record)
        by_year[year].append(record)

    sequence = []
    for year in sorted(by_year, reverse=True):
        ranked = sorted(by_year[year], key=lambda item: item["planted_acres"], reverse=True)
        dominant = ranked[0]
        sequence.append(
            {
                "year": year,
                "dominant_crop": dominant["crop"],
                "planted_acres": dominant["planted_acres"],
                "unit": dominant["unit"],
                "top_crops": [
                    {"crop": item["crop"], "planted_acres": item["planted_acres"]}
                    for item in ranked[:3]
                ],
            }
        )

    if not sequence:
        return _fallback("", "", "No USDA NASS planted-acreage records were returned for crop rotation context")

    previous_crop = sequence[1]["dominant_crop"] if len(sequence) > 1 else None
    unique_crops = {item["dominant_crop"] for item in sequence}
    latest_crop = sequence[0]["dominant_crop"]
    continuous_same_crop_years = 0
    for item in sequence:
        if item["dominant_crop"] != latest_crop:
            break
        continuous_same_crop_years += 1

    return {
        "rotation_sequence": sequence,
        "previous_crop": previous_crop,
        "latest_dominant_crop": latest_crop,
        "rotation_diversity_score": round(len(unique_crops) / len(sequence), 2),
        "continuous_same_crop_years": continuous_same_crop_years,
        "raw_records": sorted(raw_records, key=lambda item: (item["year"], item["planted_acres"]), reverse=True)[:40],
        "source": "USDA NASS Quick Stats planted acreage",
        "is_placeholder": False,
        "note": (
            "Crop rotation is estimated from county or state planted-acreage history. "
            "It is regional context, not field-level farmer-reported rotation."
        ),
    }


def _fallback(crop: str, state_alpha: str, note: str) -> dict:
    crops = REGIONAL_CROPS.get(state_alpha, DEFAULT_CROPS)
    selected = crop.title() if crop else crops[0]
    sequence_crops = [selected, *[item for item in crops if item != selected]][:4]
    current_year = date.today().year
    sequence = [
        {
            "year": current_year - index,
            "dominant_crop": sequence_crops[index % len(sequence_crops)],
            "planted_acres": None,
            "unit": "ACRES",
            "top_crops": [],
        }
        for index in range(4)
    ]
    return {
        "rotation_sequence": sequence,
        "previous_crop": sequence[1]["dominant_crop"] if len(sequence) > 1 else None,
        "latest_dominant_crop": sequence[0]["dominant_crop"],
        "rotation_diversity_score": round(len({item["dominant_crop"] for item in sequence}) / len(sequence), 2),
        "continuous_same_crop_years": 1,
        "raw_records": [],
        "source": "Demo crop rotation pattern",
        "is_placeholder": True,
        "note": note,
    }


def _number(value) -> float | None:
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None
