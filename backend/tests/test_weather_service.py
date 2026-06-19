from __future__ import annotations

from datetime import date

import requests

from services import weather_service


class FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code
        self.ok = 200 <= status_code < 300

    def json(self) -> dict:
        return self.payload


def test_weather_aggregates_stations_by_day() -> None:
    result = weather_service._summarize(
        (
            {"date": "2026-06-01T00:00:00", "datatype": "TMAX", "station": "A", "value": 34},
            {"date": "2026-06-01T00:00:00", "datatype": "TMAX", "station": "B", "value": 36},
            {"date": "2026-06-01T00:00:00", "datatype": "TMIN", "station": "A", "value": 20},
            {"date": "2026-06-01T00:00:00", "datatype": "PRCP", "station": "A", "value": 4},
            {"date": "2026-06-01T00:00:00", "datatype": "PRCP", "station": "B", "value": 6},
            {"date": "2026-06-02T00:00:00", "datatype": "TMAX", "station": "A", "value": 37},
            {"date": "2026-06-02T00:00:00", "datatype": "TMIN", "station": "A", "value": 22},
            {"date": "2026-06-02T00:00:00", "datatype": "PRCP", "station": "A", "value": 2},
        ),
        "FIPS:04013",
        date(2026, 6, 1),
        date(2026, 6, 2),
    )

    assert result["average_high_c"] == 36.0
    assert result["average_low_c"] == 21.0
    assert result["rainfall_mm"] == 7.0
    assert result["extreme_heat_days"] == 2
    assert result["station_count"] == 2
    assert result["observation_days"] == 2
    assert result["is_placeholder"] is False


def test_weather_fetches_bounded_noaa_sample(monkeypatch) -> None:
    calls: list[int] = []

    def fake_get(url, headers, params, timeout):
        offset = dict(params)["offset"]
        calls.append(offset)
        return FakeResponse(
            {
                "results": [{"date": "2026-06-01", "datatype": "TMAX", "value": 30}],
                "metadata": {"resultset": {"count": 5000}},
            }
        )

    monkeypatch.setattr(requests, "get", fake_get)
    weather_service._fetch_observations.cache_clear()

    results = weather_service._fetch_observations(
        "test-token", "FIPS:04013", "2026-06-01", "2026-06-02"
    )

    assert len(results) == 1
    assert calls == [1]


def test_weather_returns_labeled_fallback_without_token(monkeypatch) -> None:
    monkeypatch.delenv("NOAA_CDO_TOKEN", raising=False)

    result = weather_service.get_weather("04013")

    assert result["is_placeholder"] is True
    assert result["source"] == "Demo weather baseline"
    assert "not configured" in result["note"]


def test_weather_returns_labeled_fallback_on_noaa_error(monkeypatch) -> None:
    monkeypatch.setenv("NOAA_CDO_TOKEN", "test-token")

    def fake_get(url, headers, params, timeout):
        raise requests.Timeout("timed out")

    monkeypatch.setattr(requests, "get", fake_get)
    weather_service._fetch_observations.cache_clear()

    result = weather_service.get_weather("04013")

    assert result["is_placeholder"] is True
    assert "Timeout" in result["note"]


def test_noaa_status_does_not_expose_token(monkeypatch) -> None:
    monkeypatch.setenv("NOAA_CDO_TOKEN", "super-secret-token")

    result = weather_service.integration_status(validate=False)

    assert result["configured"] is True
    assert "super-secret-token" not in str(result)
