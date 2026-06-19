from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from functools import lru_cache
import os
from statistics import mean

import requests
import urllib3.util.connection


# NCEI's IPv6 route is unreachable from some Windows networks even when its
# IPv4 endpoint is healthy. urllib3 otherwise waits on that route before
# falling back, which can make an agent assessment appear hung.
urllib3.util.connection.HAS_IPV6 = False


BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2"
DATASET_ID = "GHCND"
DATA_TYPES = ("TMAX", "TMIN", "PRCP")
PAGE_LIMIT = 1000
REQUEST_TIMEOUT = 8
OBSERVATION_DAYS = 30


class NOAAError(RuntimeError):
    pass


def get_weather(county_fips: str | None, zipcode: str | None = None) -> dict:
    token = os.getenv("NOAA_CDO_TOKEN", "").strip()
    location_id = _location_id(county_fips, zipcode)
    if not token:
        return _fallback("NOAA_CDO_TOKEN is not configured")
    if not location_id:
        return _fallback("A valid county FIPS or ZIP code is required for NOAA data")

    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=OBSERVATION_DAYS - 1)
    try:
        results = _fetch_observations(token, location_id, start.isoformat(), end.isoformat())
        return _summarize(results, location_id, start, end)
    except NOAAError as exc:
        return _fallback(str(exc), location_id=location_id, start=start, end=end)


def integration_status(validate: bool = False) -> dict:
    token = os.getenv("NOAA_CDO_TOKEN", "").strip()
    status = {
        "provider": "NOAA Climate Data Online",
        "configured": bool(token),
        "validated": False,
        "available": None,
        "message": "NOAA_CDO_TOKEN is configured." if token else "NOAA_CDO_TOKEN is not configured.",
    }
    if not token or not validate:
        return status
    try:
        response = requests.get(
            f"{BASE_URL}/datasets/{DATASET_ID}",
            headers={"token": token},
            timeout=REQUEST_TIMEOUT,
        )
        _raise_for_noaa(response)
        status.update(
            validated=True,
            available=True,
            message="NOAA token is valid and the Daily Summaries dataset is available.",
        )
    except (requests.RequestException, NOAAError) as exc:
        message = (
            str(exc)
            if isinstance(exc, NOAAError)
            else f"NOAA validation request failed: {type(exc).__name__}"
        )
        status.update(validated=True, available=False, message=message)
    return status


@lru_cache(maxsize=256)
def _fetch_observations(token: str, location_id: str, start_date: str, end_date: str) -> tuple[dict, ...]:
    # Keep the agent responsive even when a county has many reporting stations.
    # NOAA caps each response at 1,000 records; this representative sample is
    # preferable to making the UI wait through an unbounded page sequence.
    try:
        response = requests.get(
            f"{BASE_URL}/data",
            headers={"token": token},
            params=[
                ("datasetid", DATASET_ID),
                ("locationid", location_id),
                *(("datatypeid", datatype) for datatype in DATA_TYPES),
                ("startdate", start_date),
                ("enddate", end_date),
                ("units", "metric"),
                ("limit", PAGE_LIMIT),
                ("offset", 1),
            ],
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise NOAAError(f"NOAA request failed: {type(exc).__name__}") from exc

    _raise_for_noaa(response)
    try:
        payload = response.json()
    except ValueError as exc:
        raise NOAAError("NOAA returned an invalid JSON response") from exc
    results = payload.get("results", [])
    if not isinstance(results, list):
        raise NOAAError("NOAA returned an unexpected data response")
    return tuple(results)


def _summarize(results: tuple[dict, ...], location_id: str, start: date, end: date) -> dict:
    daily: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: {"TMAX": [], "TMIN": [], "PRCP": []}
    )
    stations: set[str] = set()
    usable_observations = 0

    for result in results:
        datatype = result.get("datatype")
        observation_date = str(result.get("date", ""))[:10]
        if datatype not in DATA_TYPES or not observation_date:
            continue
        try:
            value = float(result["value"])
        except (KeyError, TypeError, ValueError):
            continue
        daily[observation_date][datatype].append(value)
        usable_observations += 1
        if result.get("station"):
            stations.add(str(result["station"]))

    if not daily or usable_observations == 0:
        raise NOAAError("NOAA returned no usable daily observations for this location and period")

    daily_highs = [mean(values["TMAX"]) for values in daily.values() if values["TMAX"]]
    daily_lows = [mean(values["TMIN"]) for values in daily.values() if values["TMIN"]]
    daily_precipitation = [mean(values["PRCP"]) for values in daily.values() if values["PRCP"]]

    return {
        "average_high_c": round(mean(daily_highs), 1) if daily_highs else None,
        "average_low_c": round(mean(daily_lows), 1) if daily_lows else None,
        "rainfall_mm": round(sum(daily_precipitation), 1) if daily_precipitation else None,
        "extreme_heat_days": sum(1 for value in daily_highs if value >= 35),
        "observation_days": len(daily),
        "observation_count": usable_observations,
        "station_count": len(stations),
        "period_start": start.isoformat(),
        "period_end": end.isoformat(),
        "location_id": location_id,
        "source": "NOAA Climate Data Online (GHCND Daily Summaries)",
        "is_placeholder": False,
        "note": None,
    }


def _raise_for_noaa(response: requests.Response) -> None:
    if response.ok:
        return
    if response.status_code in (401, 403):
        raise NOAAError("NOAA rejected the configured token")
    if response.status_code == 429:
        raise NOAAError("NOAA request limit was reached; try again later")
    detail = ""
    try:
        payload = response.json()
        detail = payload.get("message") or payload.get("errorMessage") or ""
    except ValueError:
        pass
    suffix = f": {detail}" if detail else ""
    raise NOAAError(f"NOAA returned HTTP {response.status_code}{suffix}")


def _location_id(county_fips: str | None, zipcode: str | None) -> str | None:
    if county_fips and len(county_fips) == 5 and county_fips.isdigit():
        return f"FIPS:{county_fips}"
    if zipcode and len(zipcode) == 5 and zipcode.isdigit():
        return f"ZIP:{zipcode}"
    return None


def _fallback(
    note: str,
    location_id: str | None = None,
    start: date | None = None,
    end: date | None = None,
) -> dict:
    return {
        "average_high_c": 31.5,
        "average_low_c": 18.2,
        "rainfall_mm": 42.0,
        "extreme_heat_days": 3,
        "observation_days": 0,
        "observation_count": 0,
        "station_count": 0,
        "period_start": start.isoformat() if start else None,
        "period_end": end.isoformat() if end else None,
        "location_id": location_id,
        "source": "Demo weather baseline",
        "is_placeholder": True,
        "note": note,
    }
