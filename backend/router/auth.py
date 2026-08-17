# backend/router/auth.py
import msal
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from auth.delegated_token_store import save_cache
from auth.oauth import build_auth_code_flow, complete_auth_code_flow
from core.settings import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login(request: Request):
    flow = build_auth_code_flow()
    request.session["auth_flow"] = flow
    return RedirectResponse(flow["auth_uri"])


@router.get("/callback")
async def callback(request: Request):
    flow = request.session.get("auth_flow")
    if not flow:
        return RedirectResponse("/?error=session_expired")

    cache = msal.SerializableTokenCache()
    result = complete_auth_code_flow(flow, dict(request.query_params), cache)
    request.session.pop("auth_flow", None)

    if "id_token_claims" not in result:
        logger.error(f"Login failed: {result.get('error_description')}")
        return RedirectResponse("/?error=login_failed")

    claims = result["id_token_claims"]
    user = {
        "email": claims.get("preferred_username") or claims.get("email"),
        "name": claims.get("name"),
    }

    # Cookie holds identity only. The actual delegated tokens live
    # server-side, keyed by this email — see auth/delegated_token_store.py.
    save_cache(user["email"], cache.serialize())
    request.session["user"] = user

    logger.info(f"User logged in: {user['email']}")
    return RedirectResponse("/chat.html")


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    settings = get_settings()
    ms_logout_url = (
        f"https://login.microsoftonline.com/{settings.AZURE_AD_TENANT_ID}"
        f"/oauth2/v2.0/logout?post_logout_redirect_uri=http://localhost:8000/"
    )
    return RedirectResponse(ms_logout_url)


@router.get("/me")
async def me(request: Request):
    user = request.session.get("user")
    return {"authenticated": user is not None, "user": user}