from __future__ import annotations

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
        response = requests.get(
            "https://api.census.gov/data/2020/dec/pl",
            params={"get": "NAME", "for": "county:*", "in": f"state:{state[1]}"},
            timeout=8,
        )
        response.raise_for_status()
        rows = response.json()
        values = [
            {
                "name": row[0].split(",", 1)[0],
                "fips": f"{row[1]}{row[2]}",
            }
            for row in rows[1:]
        ]
        return sorted(values, key=lambda item: item["name"]), False
    except (requests.RequestException, ValueError, IndexError):
        fallback = FALLBACK_COUNTIES.get(state_name, [(f"{state_name} (statewide)", state[1])])
        return [{"name": name, "fips": fips} for name, fips in fallback], True


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
