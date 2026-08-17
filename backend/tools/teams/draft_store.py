# backend/tools/teams/draft_store.py
_pending_drafts: dict[str, dict] = {}

def save_draft(user_email: str, draft: dict) -> None:
    _pending_drafts[user_email.lower()] = draft

def get_draft(user_email: str) -> dict | None:
    return _pending_drafts.get(user_email.lower())

def clear_draft(user_email: str) -> None:
    _pending_drafts.pop(user_email.lower(), None)