# backend/tools/mail/draft_store.py
"""
Minimal in-memory store for pending mail drafts, keyed by user email.
This is what makes HITL possible: draft_mail() stores a draft here
without sending anything; confirm_send_mail() reads it back only
after the user explicitly approves.

NOTE: in-memory means drafts are lost on server restart, and this
won't work across multiple backend processes/replicas. Fine for
phase 1 / single-instance learning setup — swap for Redis or a DB
table if you scale beyond one process later.
"""

_pending_drafts: dict[str, dict] = {}


def save_draft(user_email: str, draft: dict) -> None:
    _pending_drafts[user_email.lower()] = draft


def get_draft(user_email: str) -> dict | None:
    return _pending_drafts.get(user_email.lower())


def clear_draft(user_email: str) -> None:
    _pending_drafts.pop(user_email.lower(), None)