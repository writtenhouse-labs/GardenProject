from __future__ import annotations

import csv
import json
from collections import defaultdict
from functools import lru_cache
from io import BytesIO, TextIOWrapper
from pathlib import Path
from zipfile import ZipFile

import requests


STATE_FIPS = {
    "Alabama": ("AL", "01"), "Alaska": ("AK", "02"), "Arizona": ("AZ", "04"),
    "Arkansas": ("AR", "05"), "California": ("CA", "06"), "Colorado": ("CO", "08"),
    "Connecticut": ("CT", "09"), "Delaware": ("DE", "10"), "District of Columbia": ("DC", "11"),
    "Florida": ("FL", "12"), "Georgia": ("GA", "13"), "Hawaii": ("HI", "15"),
    "Idaho": ("ID", "16"), "Illinois": ("IL", "17"), "Indiana": ("IN", "18"),
    "Iowa": ("IA", "19"), "Kansas": ("KS", "20"), "Kentucky": ("KY", "21"),
    "Louisiana": ("LA", "22"), "Maine": ("ME", "23"), "Maryland": ("MD", "24"),
    "Massachusetts": ("MA", "25"), "Michigan": ("MI", "26"), "Minnesota": ("MN", "27"),
    "Mississippi": ("MS", "28"), "Missouri": ("MO", "29"), "Montana": ("MT", "30"),
    "Nebraska": ("NE", "31"), "Nevada": ("NV", "32"), "New Hampshire": ("NH", "33"),
    "New Jersey": ("NJ", "34"), "New Mexico": ("NM", "35"), "New York": ("NY", "36"),
    "North Carolina": ("NC", "37"), "North Dakota": ("ND", "38"), "Ohio": ("OH", "39"),
    "Oklahoma": ("OK", "40"), "Oregon": ("OR", "41"), "Pennsylvania": ("PA", "42"),
    "Rhode Island": ("RI", "44"), "South Carolina": ("SC", "45"), "South Dakota": ("SD", "46"),
    "Tennessee": ("TN", "47"), "Texas": ("TX", "48"), "Utah": ("UT", "49"),
    "Vermont": ("VT", "50"), "Virginia": ("VA", "51"), "Washington": ("WA", "53"),
    "West Virginia": ("WV", "54"), "Wisconsin": ("WI", "55"), "Wyoming": ("WY", "56"),
    "American Samoa": ("AS", "60"), "Guam": ("GU", "66"),
    "Northern Mariana Islands": ("MP", "69"), "Puerto Rico": ("PR", "72"),
    "U.S. Virgin Islands": ("VI", "78"),
}

FALLBACK_COUNTIES = {
    "Arizona": [("Maricopa County", "04013"), ("Pima County", "04019"), ("Yuma County", "04027")],
    "California": [("Fresno County", "06019"), ("Kern County", "06029"), ("Tulare County", "06107")],
    "Iowa": [("Polk County", "19153"), ("Story County", "19169"), ("Woodbury County", "19193")],
    "Texas": [("Harris County", "48201"), ("Lubbock County", "48303"), ("Nueces County", "48355")],
}

COUNTY_GAZETTEER_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_Gaz_counties_national.zip"
COUNTIES_PATH = Path(__file__).resolve().parents[1] / "data" / "counties.json"


def states() -> list[dict[str, str]]:
    return [
        {"name": name, "abbreviation": values[0], "fips": values[1]}
        for name, values in STATE_FIPS.items()
    ]


def counties(state_name: str) -> tuple[list[dict[str, str]], bool]:
    state = STATE_FIPS.get(state_name)
    if not state:
        return [], True
    try:
        values = _counties_by_state().get(state[0], [])
        if values:
            return values, False
    except (requests.RequestException, ValueError, IndexError):
        pass
    fallback = FALLBACK_COUNTIES.get(state_name, [(f"{state_name} (statewide)", state[1])])
    return [{"name": name, "fips": fips} for name, fips in fallback], True


def warm_county_cache() -> None:
    _counties_by_state()


@lru_cache(maxsize=1)
def _gazetteer_rows() -> tuple[dict[str, str], ...]:
    if COUNTIES_PATH.exists():
        with COUNTIES_PATH.open(encoding="utf-8-sig") as file:
            return tuple(json.load(file))
    response = requests.get(COUNTY_GAZETTEER_URL, timeout=12)
    response.raise_for_status()
    with ZipFile(BytesIO(response.content)) as archive:
        entry_name = archive.namelist()[0]
        with archive.open(entry_name) as file:
            reader = csv.DictReader(TextIOWrapper(file, encoding="utf-8"), delimiter="\t")
            return tuple(reader)


@lru_cache(maxsize=1)
def _counties_by_state() -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in _gazetteer_rows():
        state_alpha = row.get("state") or row.get("USPS")
        name = row.get("name") or row.get("NAME")
        fips = row.get("fips") or row.get("GEOID")
        if not state_alpha or not name or not fips:
            continue
        grouped[state_alpha].append(
            {
                "name": name,
                "fips": fips,
                "latitude": _number(row.get("latitude") or row.get("INTPTLAT")),
                "longitude": _number(row.get("longitude") or row.get("INTPTLONG")),
            }
        )
    return {
        state_alpha: sorted(values, key=lambda item: item["name"])
        for state_alpha, values in grouped.items()
    }


def _number(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def state_details(state_name: str) -> tuple[str, str]:
    return STATE_FIPS.get(state_name, ("", ""))


def state_from_zipcode(zipcode: str) -> str:
    try:
        response = requests.get(f"https://api.zippopotam.us/us/{zipcode}", timeout=6)
        response.raise_for_status()
        abbreviation = response.json()["places"][0]["state abbreviation"]
        return next((name for name, values in STATE_FIPS.items() if values[0] == abbreviation), "")
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return ""
