# frontend/app.py
import requests
import streamlit as st

API_URL = "http://localhost:8000/chat"

st.set_page_config(page_title="Outlook Mail Agent", page_icon="📧")
st.title("📧 Outlook Mail Agent")

if "history" not in st.session_state:
    st.session_state.history = []  # [{"role": "user"|"assistant", "content": str}]

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask me to send an email...")

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
                    },
                    timeout=60,
                )
                response.raise_for_status()
                reply = response.json()["reply"]
            except Exception as e:
                reply = f"Error contacting backend: {e}"

            st.markdown(reply)

    st.session_state.history.append({"role": "assistant", "content": reply})