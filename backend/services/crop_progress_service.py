from __future__ import annotations

from datetime import date
from functools import lru_cache
import os
import re

import requests


QUICK_STATS_URL = "https://quickstats.nass.usda.gov/api/api_GET/"
REQUEST_TIMEOUT = 15
COMPARISON_TOLERANCE = 5.0

STAGES = {
    "Corn": ["emergence", "vegetative growth", "tasseling", "grain fill", "maturity"],
    "Cotton": ["emergence", "early vegetative growth", "squaring", "boll development", "maturity"],
    "Soybeans": ["emergence", "vegetative growth", "flowering", "pod fill", "maturity"],
    "Wheat": ["emergence", "tillering", "heading", "grain fill", "maturity"],
}

STAGE_PRIORITY = {
    "PLANTED": 10,
    "EMERGED": 20,
    "JOINTED": 30,
    "HEADED": 40,
    "SILKING": 40,
    "BLOOMING": 40,
    "SQUARING": 40,
    "SETTING PODS": 50,
    "DOUGH": 55,
    "DENTED": 60,
    "BOLLS OPENING": 60,
    "COLORING": 60,
    "MATURE": 70,
    "HARVESTED": 80,
}


def assess(
    crop: str,
    state_alpha: str,
    state_name: str,
    planting_month: int | None,
    growing_season: str | None,
    today: date | None = None,
) -> dict:
    today = today or date.today()
    key = os.getenv("USDA_NASS_API_KEY", "").strip()
    if not key or not state_alpha:
        reason = (
            "USDA_NASS_API_KEY is not configured"
            if not key
            else "State information is unavailable for the USDA query"
        )
        return _fallback(crop, planting_month, growing_season, reason)

    try:
        rows, data_year = _latest_weekly_rows(key, crop.upper(), state_alpha, today.year)
        return _summarize(rows, crop, state_name, data_year)
    except CropProgressUnavailable as exc:
        return _fallback(crop, planting_month, growing_season, str(exc))


class CropProgressUnavailable(RuntimeError):
    pass


@lru_cache(maxsize=256)
def _query_year(key: str, crop: str, state_alpha: str, year: int) -> tuple[dict, ...]:
    try:
        response = requests.get(
            QUICK_STATS_URL,
            params={
                "key": key,
                "commodity_desc": crop,
                "state_alpha": state_alpha,
                "year": year,
                "freq_desc": "WEEKLY",
                "format": "JSON",
            },
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise CropProgressUnavailable(
            f"USDA NASS crop progress request failed: {type(exc).__name__}"
        ) from exc

    if response.status_code == 400:
        raise CropProgressUnavailable(
            "USDA NASS does not publish a compatible weekly progress series "
            f"for {crop.title()} in {state_alpha}"
        )
    if response.status_code in (401, 403):
        raise CropProgressUnavailable("USDA NASS rejected the configured API key")
    try:
        response.raise_for_status()
        rows = response.json().get("data", [])
    except (requests.RequestException, ValueError) as exc:
        raise CropProgressUnavailable(
            f"USDA NASS crop progress data was unavailable: {type(exc).__name__}"
        ) from exc
    return tuple(row for row in rows if row.get("agg_level_desc") == "STATE")


def _latest_weekly_rows(
    key: str,
    crop: str,
    state_alpha: str,
    current_year: int,
) -> tuple[tuple[dict, ...], int]:
    for year in (current_year, current_year - 1):
        rows = _query_year(key, crop, state_alpha, year)
        progress_rows = tuple(
            row for row in rows if str(row.get("statisticcat_desc", "")).startswith("PROGRESS")
        )
        if progress_rows:
            return progress_rows, year
    raise CropProgressUnavailable(
        f"No weekly USDA crop progress records were returned for {crop.title()} in {state_alpha}"
    )


def _summarize(rows: tuple[dict, ...], crop: str, state_name: str, data_year: int) -> dict:
    current_rows = [row for row in rows if row.get("statisticcat_desc") == "PROGRESS"]
    if not current_rows:
        raise CropProgressUnavailable("USDA returned no current crop progress estimates")

    latest_week = max(row.get("week_ending", "") for row in current_rows)
    week_rows = [row for row in rows if row.get("week_ending") == latest_week]
    current_week = [row for row in week_rows if row.get("statisticcat_desc") == "PROGRESS"]
    selected = max(
        current_week,
        key=lambda row: (
            STAGE_PRIORITY.get(_stage(row), 0),
            _number(row.get("Value")) or -1,
        ),
    )
    stage = _stage(selected)
    current_value = _number(selected.get("Value"))
    unit = selected.get("unit_desc") or ""
    previous_week = _previous_week(current_rows, selected, latest_week)
    previous_year = _matching_value(week_rows, selected, "PROGRESS, PREVIOUS YEAR")
    five_year = _matching_value(week_rows, selected, "PROGRESS, 5 YEAR AVG")
    benchmark = five_year if five_year is not None else previous_year
    status = _status(current_value, benchmark)
    condition = _condition_summary(rows, latest_week)

    return {
        "estimated_growth_stage": stage.lower(),
        "progress_status": status,
        "latest_week_ending": latest_week,
        "data_year": data_year,
        "stage_percent": current_value,
        "stage_unit": unit,
        "last_week": _comparison_text(previous_week, unit, latest_week=False),
        "last_year": _comparison_text(previous_year, unit),
        "five_year_average": _comparison_text(five_year, unit),
        "condition": condition,
        "scope": f"{state_name} state-level regional benchmark",
        "is_placeholder": False,
        "source": "USDA NASS Quick Stats weekly Crop Progress",
        "note": (
            f"USDA publishes this weekly estimate at the state level. "
            f"{state_name} is used as the regional benchmark for the selected county or ZIP code."
        ),
    }


def _previous_week(current_rows: list[dict], selected: dict, latest_week: str) -> float | None:
    matching = [
        row
        for row in current_rows
        if row.get("unit_desc") == selected.get("unit_desc")
        and row.get("week_ending", "") < latest_week
    ]
    if not matching:
        return None
    prior = max(matching, key=lambda row: row.get("week_ending", ""))
    return _number(prior.get("Value"))


def _matching_value(rows: list[dict], selected: dict, category: str) -> float | None:
    match = next(
        (
            row
            for row in rows
            if row.get("statisticcat_desc") == category
            and row.get("unit_desc") == selected.get("unit_desc")
        ),
        None,
    )
    return _number(match.get("Value")) if match else None


def _condition_summary(rows: tuple[dict, ...], latest_week: str) -> dict | None:
    condition_rows = [
        row
        for row in rows
        if row.get("statisticcat_desc") == "CONDITION"
        and row.get("week_ending", "") <= latest_week
    ]
    if not condition_rows:
        return None
    condition_week = max(row.get("week_ending", "") for row in condition_rows)
    ratings = {
        _condition_label(row): _number(row.get("Value"))
        for row in condition_rows
        if row.get("week_ending") == condition_week
    }
    return {
        "week_ending": condition_week,
        "ratings_percent": {key: value for key, value in ratings.items() if key and value is not None},
        "good_to_excellent_percent": round(
            (ratings.get("Good") or 0) + (ratings.get("Excellent") or 0), 1
        ),
    }


def _stage(row: dict) -> str:
    unit = str(row.get("unit_desc", "")).upper()
    return re.sub(r"^PCT\s+", "", unit).strip() or "PROGRESS"


def _condition_label(row: dict) -> str:
    unit = str(row.get("unit_desc", "")).upper()
    value = re.sub(r"^PCT\s+", "", unit).strip().replace("_", " ")
    return value.title()


def _status(current: float | None, benchmark: float | None) -> str:
    if current is None or benchmark is None:
        return "On Track"
    difference = current - benchmark
    if difference > COMPARISON_TOLERANCE:
        return "Ahead"
    if difference < -COMPARISON_TOLERANCE:
        return "Behind"
    return "On Track"


def _comparison_text(value: float | None, unit: str, latest_week: bool = True) -> str | None:
    if value is None:
        return None
    label = unit.lower().replace("pct ", "").replace("_", " ")
    prefix = "" if latest_week else "Prior week: "
    return f"{prefix}{value:g}% {label}"


def _number(value) -> float | None:
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def _fallback(
    crop: str,
    planting_month: int | None,
    growing_season: str | None,
    note: str,
) -> dict:
    month = planting_month or {"Cool season": 10, "Warm season": 4, "Year-round": 1}.get(
        growing_season or "", 4
    )
    elapsed = (date.today().month - month) % 12
    stage_index = min(max(elapsed // 2, 0), 4)
    stages = STAGES.get(
        crop.title(),
        ["establishment", "vegetative growth", "reproductive growth", "development", "maturity"],
    )
    status = "Ahead" if elapsed > 8 else "Behind" if elapsed == 0 else "On Track"
    return {
        "estimated_growth_stage": stages[stage_index],
        "progress_status": status,
        "latest_week_ending": None,
        "data_year": None,
        "stage_percent": None,
        "stage_unit": None,
        "last_week": "Estimated 4–7% development gain",
        "last_year": None,
        "five_year_average": None,
        "condition": None,
        "scope": "Local demo phenology estimate",
        "is_placeholder": True,
        "source": "Demo phenology model",
        "note": note,
    }
