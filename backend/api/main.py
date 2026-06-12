from fastapi import FastAPI

from api.schemas import LoginRequest, ResumeApplication, StubResponse, UserRegistration
from services.applications import submit_application
from services.database import get_database_settings
from services.users import get_profile, login_user, register_user

app = FastAPI(title="GardenProject API")


@app.get("/health")
def health() -> dict[str, str | bool]:
    database = get_database_settings()
    return {
        "status": "ok",
        "database_configured": database.configured,
    }


@app.post("/users/register", response_model=StubResponse)
def register(request: UserRegistration) -> dict[str, str]:
    return register_user(request)


@app.post("/auth/login", response_model=StubResponse)
def login(request: LoginRequest) -> dict[str, str]:
    return login_user(request)


@app.get("/users/profile")
def profile(email: str) -> dict[str, str]:
    return get_profile(email)


@app.post("/careers/apply", response_model=StubResponse)
def apply(request: ResumeApplication) -> dict[str, str]:
    return submit_application(request)
