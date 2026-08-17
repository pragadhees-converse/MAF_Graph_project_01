# frontend/config.py

# Azure App Registration

CLIENT_ID = "YOUR_CLIENT_ID"

TENANT_ID = "YOUR_TENANT_ID"

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

# Must exactly match Azure App Registration
REDIRECT_URI = "http://localhost:8501"

SCOPES = [
    "User.Read",
]