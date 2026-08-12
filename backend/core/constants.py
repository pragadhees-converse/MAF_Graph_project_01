# backend/core/constants.py
# add this near the top, alongside GRAPH_BASE_URL etc.
SYSTEM_MAILBOX = "notification@conversedatasolutions.com"  # ← set to your real system mailbox
COMPANY_DOMAIN = "conversedatasolutions.com"
GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
GRAPH_SEND_MAIL_ENDPOINT = "/users/{mailbox}/sendMail"

GRAPH_SCOPE = "https://graph.microsoft.com/.default"

DEFAULT_TIMEOUT_SECONDS = 15
MAX_RETRIES = 3
BACKOFF_BASE_SECONDS = 1.5

RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}
SUCCESS_STATUS_CODES = {200, 201, 202, 204}

SUBJECT_MAX_LENGTH = 150
BODY_MAX_LENGTH = 20000

# --- Single-tenant, single-company setup for phase 1 ---
# No company_id/environment is asked of the user or the LLM anymore.
# These fixed values replace the old COMPANY_REGISTRY lookup. If you
# add a second company/tenant later, this is the file to expand again.
TENANT_ID = "768a0b79-31e7-4458-901b-11417f553618"
MAILBOX_DOMAIN = "conversedatasolutions.com"