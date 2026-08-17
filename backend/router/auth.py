from fastapi import APIRouter
from fastapi.responses import RedirectResponse

import msal

from core.settings import get_settings

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.get("/login")
async def login():

    settings = get_settings()

    authority = (
        f"https://login.microsoftonline.com/"
        f"{settings.AZURE_AD_TENANT_ID}"
    )

    app = msal.ConfidentialClientApplication(
        client_id=settings.AZURE_AD_CLIENT_ID,
        client_credential=settings.AZURE_AD_CLIENT_SECRET,
        authority=authority,
    )

    auth_url = app.get_authorization_request_url(
        scopes=[
            "openid",
            "profile",
            "email",
            "User.Read",
        ],
        redirect_uri=settings.AZURE_REDIRECT_URI,
    )

    return RedirectResponse(auth_url)