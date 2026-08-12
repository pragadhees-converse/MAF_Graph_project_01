# backend/../frontend/app.py
import requests
import streamlit as st

API_URL = "http://localhost:8000/chat"
COMPANY_DOMAIN = "conversedatasolutions.com"

st.set_page_config(page_title="Outlook Mail Agent", page_icon="📧")

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if not st.session_state.user_email:
    st.title("🔐 Login")
    email_input = st.text_input("Enter your company email")
    if st.button("Login"):
        if email_input.lower().endswith(f"@{COMPANY_DOMAIN}"):
            st.session_state.user_email = email_input.lower()
            st.rerun()
        else:
            st.error(f"Please use your @{COMPANY_DOMAIN} email address.")
    st.stop()

st.title("📧 Outlook Mail Agent")
st.caption(f"Logged in as {st.session_state.user_email}")

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask me anything, or ask me to email you something...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    API_URL,
                    json={
                        "message": user_input,
                        "history": st.session_state.history[:-1],
                        "user_email": st.session_state.user_email,
                    },
                    timeout=60,
                )
                response.raise_for_status()
                reply = response.json()["reply"]
            except Exception as e:
                reply = f"Error contacting backend: {e}"
            st.markdown(reply)

    st.session_state.history.append({"role": "assistant", "content": reply})