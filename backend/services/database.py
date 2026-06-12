import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseSettings:
    url: str
    configured: bool


def get_database_settings() -> DatabaseSettings:
    url = os.getenv("GARDENPROJECT_DATABASE_URL", "")
    return DatabaseSettings(url=url, configured=bool(url))


class DatabaseConnection:
    """Placeholder for the future employee portal database adapter."""

    def __init__(self, settings: DatabaseSettings | None = None) -> None:
        self.settings = settings or get_database_settings()

    def connect(self) -> None:
        raise NotImplementedError("Database connection is stubbed for the initial scaffold.")

    def close(self) -> None:
        return None
