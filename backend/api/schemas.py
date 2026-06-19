from pydantic import BaseModel, EmailStr, Field


class UserRegistration(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    role: str = Field(..., pattern="^(employee|applicant)$")
    salary: float | None = None
    ssn: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class ResumeApplication(BaseModel):
    applicant_name: str = Field(..., min_length=1)
    applicant_position: str = ""
    resume_filename: str = Field(..., min_length=1)


class StubResponse(BaseModel):
    status: str
    message: str


class CropAssessmentRequest(BaseModel):
    state: str | None = None
    county: str | None = None
    county_fips: str | None = None
    zipcode: str | None = Field(default=None, pattern=r"^\d{5}$")
    crop: str = Field(..., min_length=1)
    planting_month: int | None = Field(default=None, ge=1, le=12)
    growing_season: str | None = None
    irrigation: str | None = None
    soil_type: str | None = None
    field_size: float | None = Field(default=None, gt=0)
    objective: str = "Monitor progress"
