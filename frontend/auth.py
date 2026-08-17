import streamlit as st
import msal

from config import (
    CLIENT_ID,
    AUTHORITY,
    REDIRECT_URI,
    SCOPES,
)


class AuthService:

    def __init__(self):

        self.app = msal.PublicClientApplication(
            client_id=CLIENT_ID,
            authority=AUTHORITY,
        )

    def login(self):

        # Already logged in

        if "access_token" in st.session_state:
            return st.session_state.access_token

        flow = self.app.initiate_device_flow(
            scopes=SCOPES
        )

        if "user_code" not in flow:
            st.error("Unable to start Microsoft login.")
            st.stop()

        st.info(
            f"""
Go to

{flow['verification_uri']}

and enter the code

{flow['user_code']}
"""
        )

        result = self.app.acquire_token_by_device_flow(flow)

        if "access_token" not in result:

            st.error(
                result.get(
                    "error_description",
                    "Microsoft Login Failed",
                )
            )

            st.stop()

        st.session_state.access_token = result["access_token"]

        return result["access_token"]


auth_service = AuthService()