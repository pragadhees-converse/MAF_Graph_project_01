# backend/auth/delegated_token_store.py
"""
In-memory store for each logged-in user's serialized MSAL token cache.
Keyed by email. This is what lets us act as the user for Teams calls
without storing raw tokens in the browser cookie.

NOTE: same caveat as draft_store.py — in-memory means this resets on
server restart and doesn't work across multiple processes/replicas.
Fine for single-instance phase 1; swap for Redis/DB if you scale out.
"""

_token_caches: dict[str, str] = {}


def save_cache(user_email: str, serialized_cache: str) -> None:
    _token_caches[user_email.lower()] = serialized_cache


def get_cache(user_email: str) -> str | None:
    return _token_caches.get(user_email.lower())