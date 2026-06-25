from fastapi.testclient import TestClient

from api.main import app
from services.assessment_store import clear


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_crop_intelligence_options_lists_states() -> None:
    client = TestClient(app)
    response = client.get("/crop-intelligence/options")

    assert response.status_code == 200
    assert any(item["name"] == "Arizona" for item in response.json()["states"])


def test_noaa_status_reports_configuration_without_exposing_token(monkeypatch) -> None:
    monkeypatch.setenv("NOAA_CDO_TOKEN", "private-test-token")
    client = TestClient(app)

    response = client.get("/integrations/noaa/status")

    assert response.status_code == 200
    assert response.json()["configured"] is True
    assert "private-test-token" not in response.text


def test_crop_intelligence_assessment_works_with_fallback_data() -> None:
    clear()
    client = TestClient(app)
    response = client.post(
        "/crop-intelligence/assess",
        json={
            "state": "Arizona",
            "county": "Maricopa County",
            "latitude": 33.4484,
            "longitude": -112.074,
            "location_precision": "point",
            "point_geojson": {"type": "Point", "coordinates": [-112.074, 33.4484]},
            "crop": "Cotton",
            "planting_month": 3,
            "objective": "Monitor progress",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["crop_status"]["crop"] == "Cotton"
    assert payload["field_location"]["location_precision"] == "point"
    assert payload["field_location"]["point_geojson"]["type"] == "Point"
    assert len(payload["risk_assessment"]) == 4
    assert payload["data_quality"]["uses_placeholder_data"] is True
    assert set(payload["integration_results"]) == {
        "crop_progress",
        "weather",
        "drought",
        "yield_history",
        "crop_rotation",
        "similarity",
    }

    latest_response = client.get("/crop-intelligence/latest")
    assert latest_response.status_code == 200
    assert latest_response.json()["available"] is True
    assert latest_response.json()["assessment"]["crop_status"]["crop"] == "Cotton"


def test_latest_assessment_is_replaced_by_next_run() -> None:
    clear()
    client = TestClient(app)
    base_request = {
        "state": "Arizona",
        "county": "Maricopa County",
        "planting_month": 3,
        "objective": "Monitor progress",
    }

    client.post("/crop-intelligence/assess", json={**base_request, "crop": "Cotton"})
    client.post("/crop-intelligence/assess", json={**base_request, "crop": "Barley"})

    latest_response = client.get("/crop-intelligence/latest")
    assert latest_response.json()["assessment"]["crop_status"]["crop"] == "Barley"


def test_crop_intelligence_assessment_allows_unknown_crop_boundary_mode() -> None:
    clear()
    client = TestClient(app)
    response = client.post(
        "/crop-intelligence/assess",
        json={
            "state": "Arizona",
            "county": "Maricopa County",
            "latitude": 33.389386,
            "longitude": -112.510453,
            "location_precision": "boundary",
            "field_boundary_geojson": {
                "type": "Polygon",
                "coordinates": [[
                    [-112.511, 33.389],
                    [-112.51, 33.389],
                    [-112.51, 33.39],
                    [-112.511, 33.389],
                ]],
            },
            "crop": "Unknown / identify from boundary",
            "planting_month": 3,
            "objective": "Monitor progress",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["crop_status"]["progress_status"] == "Location context only"
    assert payload["field_location"]["location_precision"] == "boundary"
    assert payload["integration_results"]["crop_progress"]["is_placeholder"] is False
    assert payload["integration_results"]["yield_history"]["records"] == []
    assert "crop identification" in payload["agent_summary"].lower()
