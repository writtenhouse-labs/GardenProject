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
