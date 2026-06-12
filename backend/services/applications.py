from api.schemas import ResumeApplication


def submit_application(_request: ResumeApplication) -> dict[str, str]:
    return {
        "status": "stubbed",
        "message": "Application endpoint is wired, but resume storage is not implemented yet.",
    }
