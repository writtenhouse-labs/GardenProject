from api.schemas import LoginRequest, UserRegistration


def register_user(_request: UserRegistration) -> dict[str, str]:
    return {
        "status": "stubbed",
        "message": "Registration endpoint is wired, but persistence is not implemented yet.",
    }


def login_user(_request: LoginRequest) -> dict[str, str]:
    return {
        "status": "stubbed",
        "message": "Login endpoint is wired, but credential storage is not implemented yet.",
    }


def get_profile(email: str) -> dict[str, str]:
    return {
        "email": email,
        "first_name": "Sample",
        "last_name": "User",
        "address": "123 Garden Way",
        "phone": "555-1234",
        "salary": "",
        "ssn": "",
        "role": "applicant",
    }
