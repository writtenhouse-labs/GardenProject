from __future__ import annotations

from copy import deepcopy
from threading import Lock


_lock = Lock()
_latest_assessment: dict | None = None


def save(assessment: dict) -> dict:
    global _latest_assessment
    with _lock:
        _latest_assessment = deepcopy(assessment)
        return deepcopy(_latest_assessment)


def latest() -> dict | None:
    with _lock:
        return deepcopy(_latest_assessment)


def clear() -> None:
    global _latest_assessment
    with _lock:
        _latest_assessment = None
