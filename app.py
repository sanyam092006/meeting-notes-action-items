import streamlit as st

from components import MAX_NOTES_CHARS, quota_ok, render_chat, render_results, render_sidebar
from llm import extract
from prompts import SAMPLE_NOTES
from schemas import summary_to_markdown

st.set_page_config(page_title="Meeting Notes to Action Items", page_icon="📝", layout="wide")
st.title("📝 Meeting Notes → Action Items")
st.caption("Paste notes, get structured action items, then ask follow-up questions.")

api_key, model, using_server_key = render_sidebar()

uploaded = st.file_uploader("Upload notes (.txt)", type=["txt"])
if uploaded:
    st.session_state["notes_box"] = uploaded.read().decode("utf-8", errors="ignore")
if st.button("Use sample notes"):
    st.session_state["notes_box"] = SAMPLE_NOTES

notes = st.text_area("Meeting notes", key="notes_box", height=250, placeholder="Paste your meeting notes here...")

if st.button("Analyze", type="primary"):
    if not api_key:
        st.error("No API key available. Enter your Gemini API key in the sidebar.")
    elif not notes.strip():
        st.error("Add some meeting notes first.")
    elif len(notes) > MAX_NOTES_CHARS:
        st.error(f"Notes are too long ({len(notes)} characters). Please keep them under {MAX_NOTES_CHARS}.")
    elif quota_ok(using_server_key):
        try:
            with st.spinner("Analyzing..."):
                result = extract(notes, api_key, model)
            st.session_state["result"] = result
            # fresh follow-up chat as standard role/content messages
            st.session_state["chat"] = [
                {"role": "user", "content": f"Meeting notes:\n{notes}"},
                {"role": "assistant", "content": summary_to_markdown(result)},
            ]
        except Exception as e:
            st.error(f"Something went wrong: {e}")

if st.session_state.get("result"):
    render_results(st.session_state["result"])
    render_chat(api_key, model, using_server_key)
