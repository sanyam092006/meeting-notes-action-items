import os

import pandas as pd
import streamlit as st

from llm import call_gemini
from prompts import CHAT_SYSTEM
from schemas import MeetingSummary


MAX_REQUESTS_PER_SESSION = 10  # soft cap per visitor session when using the demo key
MAX_NOTES_CHARS = 8000  # keeps each request small


def _secret(name, default=""):
    """Read from Streamlit Cloud Secrets, falling back to an env var (local runs)."""
    try:
        return st.secrets.get(name, default)
    except Exception:
        return os.getenv(name, default)


def render_sidebar():
    """Returns (api_key, model, using_server_key)."""
    server_key = _secret("GEMINI_API_KEY")
    model = _secret("GEMINI_MODEL", "gemini-2.5-flash")
    user_key = ""
    with st.sidebar:
        st.header("Settings")
        if server_key:
            st.success("Demo key is built in. No key needed.")
            with st.expander("Use your own key instead (optional)"):
                user_key = st.text_input("Your Gemini API key", type="password")
        else:
            user_key = st.text_input("Gemini API key", type="password", help="Free key at aistudio.google.com")
        st.caption(f"Model: {model}")
        if st.button("Clear everything"):
            used = st.session_state.get("used", 0)
            st.session_state.clear()
            st.session_state["used"] = used  # clearing must not reset the usage count
            st.rerun()
    api_key = user_key or server_key
    using_server_key = bool(server_key) and not user_key
    return api_key, model, using_server_key


def quota_ok(using_server_key):
    """Soft per-session limit, applied only when the demo key is in use."""
    if not using_server_key:
        return True
    used = st.session_state.get("used", 0)
    if used >= MAX_REQUESTS_PER_SESSION:
        st.warning("Demo limit reached for this session. Paste your own free Gemini key in the sidebar to continue.")
        return False
    st.session_state["used"] = used + 1
    return True


def render_results(result: MeetingSummary):
    st.subheader("Summary")
    st.write(result.summary)

    left, right = st.columns(2)
    with left:
        st.subheader("Decisions")
        for d in result.decisions or ["None"]:
            st.markdown(f"- {d}")
    with right:
        st.subheader("Open questions")
        for q in result.open_questions or ["None"]:
            st.markdown(f"- {q}")

    st.subheader("Action items")
    df = pd.DataFrame([a.model_dump() for a in result.action_items])
    if df.empty:
        st.write("No action items found.")
        return

    df.columns = [c.title() for c in df.columns]
    st.dataframe(df, use_container_width=True, hide_index=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Total tasks", len(df))
    m2.metric("High priority", int((df["Priority"].str.lower() == "high").sum()))
    m3.metric("Unassigned", int((df["Owner"].str.lower() == "unassigned").sum()))

    st.bar_chart(df["Owner"].value_counts())
    st.download_button("Download CSV", df.to_csv(index=False), "action_items.csv", "text/csv")


def render_chat(api_key, model, using_server_key=False):
    st.divider()
    st.subheader("💬 Ask about this meeting")
    chat = st.session_state.get("chat", [])
    for m in chat[2:]:  # first two messages are the notes + summary context
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    question = st.chat_input("e.g. What is Amit responsible for?")
    if not question:
        return
    if not api_key:
        st.error("No API key available. Enter your Gemini API key in the sidebar.")
        return
    if not quota_ok(using_server_key):
        return

    chat.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                resp = call_gemini([{"role": "system", "content": CHAT_SYSTEM}] + chat, api_key, model)
            st.markdown(resp.text)
        chat.append({"role": "assistant", "content": resp.text})
        st.session_state["chat"] = chat
    except Exception as e:
        st.error(f"Something went wrong: {e}")
