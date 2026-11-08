"""Runnable local decision example; no network call is needed for the first gate."""

from src.onboarding import SignupRequest, admit_signup, audit_event


class LocalClient:
    def verify_captcha(self, widget_record_id: str, token: str, ip: str, action: str) -> dict[str, object]:
        return {"ok": True, "data": {}}

    def create_user(self, email: str, password: str, name: str, invite_code: str) -> dict[str, object]:
        return {"ok": True, "data": {"user_id": "local-user"}}

    def create_session(self, user_id: str) -> dict[str, object]:
        return {"ok": True, "data": {"session_id": "local-session"}}


request = SignupRequest("founder@example.com", "secret", "Founder", "WELCOME-42", "local", "127.0.0.1")
print(audit_event(admit_signup(request, {"WELCOME-42"}, LocalClient())))
