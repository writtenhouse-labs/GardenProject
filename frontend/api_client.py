import os

import requests


API_BASE_URL = os.getenv("GARDENPROJECT_API_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT_SECONDS = 15


def post(path: str, payload: dict) -> dict:
    response = requests.post(f"{API_BASE_URL}{path}", json=payload, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def get(path: str, params: dict | None = None) -> dict:
    response = requests.get(f"{API_BASE_URL}{path}", params=params, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()
