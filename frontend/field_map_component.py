from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


COMPONENT_DIR = Path(__file__).parent / "components" / "field_map"

_field_map = components.declare_component("field_map", path=str(COMPONENT_DIR))


def render_field_map(
    *,
    api_key: str,
    center_query: str,
    center: dict[str, float] | None = None,
    value: dict[str, Any] | None = None,
    key: str = "field_map",
) -> dict[str, Any] | None:
    return _field_map(
        api_key=api_key,
        center_query=center_query,
        center=center,
        value=value or {},
        default=value or {},
        key=key,
    )
