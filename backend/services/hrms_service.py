# backend/services/hrms_service.py
"""
Placeholder for future HRMS integration.

CURRENT PHASE: Azure AD (auth/oauth.py) provides only identity —
the logged-in user's email and display name. Nothing here is called yet.

FUTURE PHASE: once logged in, this service will call the organization's
HRMS API using the authenticated email to fetch validated employee data:
employee ID, department, designation, manager, Teams/user mapping.

This is kept as a separate service (not merged into oauth.py) so Azure AD
stays purely an identity provider, and HRMS remains the system of record
for organizational data — matching the intended production flow:

    Azure AD login -> email -> HRMS API -> employee details -> Graph ops
"""


async def get_employee_details(email: str) -> dict | None:
    # TODO: implement once HRMS API endpoint and credentials are available.
    # Should return something like:
    # {"employee_id": ..., "name": ..., "department": ..., "designation": ...,
    #  "manager": ..., "teams_user_id": ...}
    return None