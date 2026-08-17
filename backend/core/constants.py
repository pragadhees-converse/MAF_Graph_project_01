# backend/core/constants.py

# ------------------------------------------------------------------
# Application
# ------------------------------------------------------------------

SYSTEM_MAILBOX = "notification@conversedatasolutions.com"
COMPANY_DOMAIN = "conversedatasolutions.com"

# ------------------------------------------------------------------
# Microsoft Graph
# ------------------------------------------------------------------

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
GRAPH_SCOPE = "https://graph.microsoft.com/.default"

# ------------------------------------------------------------------
# Mail
# ------------------------------------------------------------------

GRAPH_SEND_MAIL_ENDPOINT = "/users/{mailbox}/sendMail"

# ------------------------------------------------------------------
# Teams
# ------------------------------------------------------------------

# Resolve a user's profile by email (User Principal Name)
GRAPH_USERS_ENDPOINT = "/users/{user_principal_name}"

# Create or reuse a one-to-one chat
GRAPH_CHATS_ENDPOINT = "/chats"

# Send a message to an existing chat
GRAPH_CHAT_MESSAGES_ENDPOINT = "/chats/{chat_id}/messages"

# ------------------------------------------------------------------
# HTTP
# ------------------------------------------------------------------

DEFAULT_TIMEOUT_SECONDS = 15

MAX_RETRIES = 3

BACKOFF_BASE_SECONDS = 1.5

SUCCESS_STATUS_CODES = {
    200,
    201,
    202,
    204,
}

RETRYABLE_STATUS_CODES = {
    408,
    429,
    500,
    502,
    503,
    504,
}

# ------------------------------------------------------------------
# Validation
# ------------------------------------------------------------------

SUBJECT_MAX_LENGTH = 150

BODY_MAX_LENGTH = 20000

TEAMS_MESSAGE_MAX_LENGTH = 4000

# ------------------------------------------------------------------
# Single Tenant (Phase 1)
# ------------------------------------------------------------------

TENANT_ID = "768a0b79-31e7-4458-901b-11417f553618"

MAILBOX_DOMAIN = "conversedatasolutions.com"

##############################################################
# Microsoft Graph Users
##############################################################

GRAPH_USER_BY_EMAIL_ENDPOINT = "/users/{user_principal_name}"

GRAPH_USER_SEARCH_ENDPOINT = (
    "/users?$filter=startswith(displayName,'{display_name}')"
)