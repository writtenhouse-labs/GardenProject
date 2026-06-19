from fastapi import FastAPI

from services.configuration import load_configuration

load_configuration()

from api.schemas import CropAssessmentRequest, LoginRequest, ResumeApplication, StubResponse, UserRegistration
from services.applications import submit_application
from services.assessment_store import latest as latest_assessment
from services.assessment_store import save as save_assessment
from services.database import get_database_settings
from services.users import get_profile, login_user, register_user
from services.crop_progress_agent import assess, get_options
from services.weather_service import integration_status

app = FastAPI(title="GardenProject API")


@app.get("/crop-intelligence/options")
def crop_intelligence_options(
    state: str | None = None,
    county: str | None = None,
    zipcode: str | None = None,
) -> dict:
    return get_options(state, county, zipcode)


@app.post("/crop-intelligence/assess")
def crop_intelligence_assess(request: CropAssessmentRequest) -> dict:
    return save_assessment(assess(request))


@app.get("/crop-intelligence/latest")
def crop_intelligence_latest() -> dict:
    assessment = latest_assessment()
    return {
        "available": assessment is not None,
        "assessment": assessment,
    }


@app.get("/integrations/noaa/status")
def noaa_status(validate: bool = False) -> dict:
    return integration_status(validate)


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
