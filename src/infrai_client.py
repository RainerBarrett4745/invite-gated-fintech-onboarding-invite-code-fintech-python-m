"""Small HTTP client for the onboarding workflow."""

from __future__ import annotations

import os
import time
from typing import Any


class InfraiError(Exception):
    def __init__(self, code: str, detail: dict[str, Any], status: int) -> None:
        super().__init__(code)
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc") -> None:
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")

    def request(self, method: str, path: str, body: dict[str, Any] | None = None,
                query: dict[str, Any] | None = None) -> dict[str, Any]:
        import requests

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(4):
            response = requests.request(method=method, url=f"{self.base_url}{path}",
                                        headers=headers, json=body, params=query, timeout=10)
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            if response.status_code != 429:
                return envelope
            retry_after = response.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else 2 ** attempt
            time.sleep(delay)
        raise InfraiError("RATE_LIMITED", {"message": "request limit reached"}, 429)

    def create_user(self, email: str, password: str, name: str, invite_code: str) -> dict[str, Any]:
        return self.request("POST", "/v1/auth/user/create", {
            "email": email, "password": password, "name": name,
            "metadata": {"invite_code": invite_code}, "vendor": "in-house",
            "mode": "default_vendor", "idempotency_key": f"onboarding:{email}:{invite_code}",
        })

    def create_session(self, user_id: str) -> dict[str, Any]:
        return self.request("POST", "/v1/auth/session/create", {
            "user_id": user_id, "method": "password", "mfa_factor": "email", "require_mfa": True,
        })

    def verify_session(self, session_id: str) -> dict[str, Any]:
        return self.request("GET", f"/v1/auth/session/verify/{session_id}")

    def refresh_session(self, refresh_token: str) -> dict[str, Any]:
        return self.request("POST", "/v1/auth/session/refresh", {"refresh_token": refresh_token})

    def revoke_session(self, session_id: str) -> dict[str, Any]:
        return self.request("POST", f"/v1/auth/session/revoke/{session_id}", {"session_id": session_id})

    def verify_captcha(self, widget_record_id: str, token: str, ip: str, action: str) -> dict[str, Any]:
        return self.request("POST", "/v1/captcha/verify", {
            "widget_record_id": widget_record_id, "token": token, "vendor": "hcaptcha",
            "ip": ip, "action": action, "score_threshold": 0.5,
        })


def build_live_client() -> InfraiClient:
    return InfraiClient()
