from src.onboarding import SignupRequest, admit_signup


class CaptchaOnlyClient:
    def verify_captcha(self, token: str, ip: str, action: str) -> dict[str, object]:
        return {"ok": True, "data": {}}


def test_invite_code_is_the_first_admission_decision() -> None:
    request = SignupRequest("founder@example.com", "secret", "Founder", "WRONG", "captcha", "127.0.0.1")
    result = admit_signup(request, {"WELCOME-42"}, CaptchaOnlyClient())
    assert result.status == "rejected"
    assert result.reason == "invite_code_required"
