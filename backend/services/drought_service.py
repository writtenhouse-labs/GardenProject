from __future__ import annotations

from datetime import date, timedelta

import requests


def get_drought(county_fips: str | None) -> dict:
    if not county_fips or len(county_fips) != 5:
        return _fallback("County FIPS is unavailable")
    end = date.today()
    start = end - timedelta(days=35)
    try:
        response = requests.get(
            "https://usdmdataservices.unl.edu/api/CountyStatistics/GetDroughtSeverityStatisticsByAreaPercent",
            headers={"Accept": "application/json"},
            params={
                "aoi": county_fips,
                "startdate": f"{start.month}/{start.day}/{start.year}",
                "enddate": f"{end.month}/{end.day}/{end.year}",
                "statisticsType": 1,
            },
            timeout=12,
        )
        response.raise_for_status()
        rows = response.json()
        latest = rows[-1] if rows else {}
        dsci = _number(latest.get("DSCI"))
        if dsci is None:
            dsci = sum(_number(latest.get(key)) or 0 for key in ("D0", "D1", "D2", "D3", "D4"))
        return {
            "dsci": round(dsci, 1),
            "category": _category(dsci),
            "source": "U.S. Drought Monitor REST service",
            "is_placeholder": False,
            "note": None,
        }
    except (requests.RequestException, ValueError, TypeError) as exc:
        return _fallback(f"U.S. Drought Monitor unavailable: {type(exc).__name__}")


def _number(value) -> float | None:
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def _category(dsci: float) -> str:
    if dsci >= 300:
        return "Extreme"
    if dsci >= 200:
        return "Severe"
    if dsci >= 100:
        return "Moderate"
    if dsci > 0:
        return "Abnormally Dry"
    return "None"


def _fallback(note: str) -> dict:
    return {
        "dsci": 85.0,
        "category": "Abnormally Dry",
        "source": "Demo drought baseline",
        "is_placeholder": True,
        "note": note,
    }
