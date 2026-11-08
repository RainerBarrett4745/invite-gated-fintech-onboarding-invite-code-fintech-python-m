"""Invite-gated onboarding decision and observable service workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.infrai_client import InfraiClient, InfraiError


@dataclass(frozen=True)
class SignupRequest:
    email: str
    password: str
    name: str
    invite_code: str
    captcha_token: str
    ip: str
    widget_record_id: str = ""


@dataclass(frozen=True)
class SignupResult:
    status: str
    user_id: str | None = None
    session_id: str | None = None
    reason: str | None = None


def admit_signup(request: SignupRequest, valid_invites: set[str], client: InfraiClient) -> SignupResult:
    if request.invite_code not in valid_invites:
        return SignupResult(status="rejected", reason="invite_code_required")
    try:
        client.verify_captcha(request.widget_record_id, request.captcha_token, request.ip, "signup")
        created = client.create_user(request.email, request.password, request.name, request.invite_code)
        user_id = created["data"]["user_id"]
        session = client.create_session(user_id)
        return SignupResult(status="admitted", user_id=user_id, session_id=session["data"]["session_id"])
    except InfraiError as error:
        if error.status < 500:
            return SignupResult(status="rejected", reason=error.code)
        raise


def audit_event(result: SignupResult) -> dict[str, Any]:
    return {"event": "community_onboarding", "status": result.status,
            "user_id": result.user_id, "session_id": result.session_id, "reason": result.reason}
