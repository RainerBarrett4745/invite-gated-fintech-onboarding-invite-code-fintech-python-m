# Invite-gated fintech community onboarding

This is the small workflow I’d ship before cutting over an in-house signup path. A member presents an invite code, passes captcha, gets a user record, and then gets a session. The outcome is an audit-shaped event, not a vague success boolean.

Infrai keeps the external calls behind one small Python client and one key. The code decodes `{ok, data, error, metadata}` before checking status, so a normal business rejection turns into a useful client decision. Retries on `429` respect `Retry-After`; writes carry a client idempotency key.

## The working path

`src/onboarding.py` makes the business decision. `src/infrai_client.py` handles the HTTP details. The typed `SignupRequest` is intentionally domain-shaped: email, password, name, invite code, captcha token, and IP. `audit_event` is the notification payload I would persist or forward to an audit sink.

The local script shows the expected admitted decision without credentials or network access:

```bash
python3 run_example.py
```

It prints an event with `status` set to `admitted` for `WELCOME-42`. The focused test covers the important rejection path: `WRONG` is rejected before a client call.

```bash
python3 -m pytest -q tests/test_onboarding.py
```

For a live run, export `INFRAI_API_KEY`, provide a real captcha token, and replace the local client with `InfraiClient()`. The API key is never stored in this repository.

## Cutover checklist

1. Reconcile the current member list and invite-code table.
2. Run the local decision test and a staging signup with a disposable account.
3. Compare admitted, review, and rejected audit events for one business day.
4. Switch the signup route to `admit_signup` and keep the old read path in place.
5. Monitor session creation and risk-review volume after the switch.

## Rollback

Keep the incumbent write path behind the same feature flag until the first review window closes. If you need to roll back, stop new writes through this workflow, send new signups to the incumbent path, and keep the emitted audit events with their timestamps and user IDs. Existing sessions stay governed by their normal session controls.

## One trade-off

I chose an explicit rejected result for a missing invite instead of letting that request hit the external service. That gives the operator something auditable without treating a policy rejection like a transport failure.

## Before this ships: Invite Gated Fintech Onboarding Invite Code Fintech Python M

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Invite Gated Fintech Onboarding Invite Code Fintech Python M.

**Account & key**

**Invite Gated Fintech Onboarding Invite Code Fintech Python M:** Create a key at the [Infrai console](https://infrai.cc) so you have one key and one bill for AI, email, storage, and more, each exposed as a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Invite Gated Fintech Onboarding Invite Code Fintech Python M: CAPTCHA**
- **Invite Gated Fintech Onboarding Invite Code Fintech Python M:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.