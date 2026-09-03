# backend/router/teams_actions.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from tools.teams.service import notify_sender_of_response
from tools.teams.tool import resolve_teams_draft
from utils.action_tokens import verify_action_token
from utils.correlation import generate_correlation_id

router = APIRouter(tags=["teams-actions"])


def _page(message: str, ok: bool) -> HTMLResponse:
    color = "#1d8a3e" if ok else "#b23"
    return HTMLResponse(f"""
    <html><body style="font-family:system-ui;text-align:center;padding-top:15vh;">
      <h2 style="color:{color};">{message}</h2>
      <p style="color:#777;">You can close this tab.</p>
    </body></html>
    """)


@router.get("/teams-action")
async def teams_action(token: str):
    payload = verify_action_token(token)
    if payload is None:
        return _page("This link has expired or is invalid.", ok=False)

    if payload["kind"] == "content_response":
        correlation_id = generate_correlation_id()
        await notify_sender_of_response(
            sender_email=payload["sender_email"],
            recipient_email=payload["recipient_email"],
            summary=payload["summary"],
            decision=payload["decision"],
            correlation_id=correlation_id,
        )
        return _page(f"Thanks — your response ({payload['decision']}) has been recorded.", ok=True)

    if payload["kind"] == "teams":
        approved = payload["decision"] == "approve"
        result = await resolve_teams_draft(payload["user_email"], approved)
        if result.get("status") == "no_draft":
            return _page("This draft was already handled or has expired.", ok=False)
        if result.get("success") or result.get("status") == "declined":
            return _page("Done.", ok=True)
        return _page(f"Something went wrong: {result.get('message', 'unknown error')}", ok=False)

    return _page("Unrecognized action type.", ok=False)