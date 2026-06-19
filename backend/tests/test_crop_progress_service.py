from __future__ import annotations

from datetime import date

from services import crop_progress_service


def _row(
    category: str,
    week: str,
    unit: str,
    value: str,
) -> dict:
    return {
        "statisticcat_desc": category,
        "week_ending": week,
        "unit_desc": unit,
        "Value": value,
        "agg_level_desc": "STATE",
    }


def test_live_progress_selects_latest_stage_and_comparisons(monkeypatch) -> None:
    rows = (
        _row("PROGRESS", "2025-09-21", "PCT HARVESTED", "19"),
        _row("PROGRESS", "2025-09-28", "PCT BOLLS OPENING", "82"),
        _row("PROGRESS", "2025-09-28", "PCT HARVESTED", "32"),
        _row("PROGRESS, PREVIOUS YEAR", "2025-09-28", "PCT HARVESTED", "43"),
        _row("PROGRESS, 5 YEAR AVG", "2025-09-28", "PCT HARVESTED", "22"),
        _row("CONDITION", "2025-09-28", "PCT GOOD", "42"),
        _row("CONDITION", "2025-09-28", "PCT EXCELLENT", "18"),
    )
    monkeypatch.setenv("USDA_NASS_API_KEY", "test-key")
    monkeypatch.setattr(
        crop_progress_service,
        "_latest_weekly_rows",
        lambda key, crop, state, year: (rows, 2025),
    )

    result = crop_progress_service.assess(
        "Cotton", "AZ", "Arizona", 3, None, today=date(2026, 6, 19)
    )

    assert result["estimated_growth_stage"] == "harvested"
    assert result["stage_percent"] == 32.0
    assert result["last_week"] == "Prior week: 19% harvested"
    assert result["last_year"] == "43% harvested"
    assert result["five_year_average"] == "22% harvested"
    assert result["progress_status"] == "Ahead"
    assert result["condition"]["good_to_excellent_percent"] == 60.0
    assert result["is_placeholder"] is False


def test_progress_falls_back_for_unsupported_crop(monkeypatch) -> None:
    monkeypatch.setenv("USDA_NASS_API_KEY", "test-key")

    def unavailable(*args):
        raise crop_progress_service.CropProgressUnavailable(
            "USDA NASS does not publish a compatible weekly progress series"
        )

    monkeypatch.setattr(crop_progress_service, "_latest_weekly_rows", unavailable)

    result = crop_progress_service.assess(
        "Beets", "AZ", "Arizona", 3, None, today=date(2026, 6, 19)
    )

    assert result["is_placeholder"] is True
    assert result["source"] == "Demo phenology model"
    assert "does not publish" in result["note"]
