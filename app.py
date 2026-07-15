
import os
import uuid
import streamlit as st
from dotenv import load_dotenv
from db.database import init_db
from agent.agent import build_agent, chat

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY not found. Make sure your .env file exists.")
    st.stop()

st.set_page_config(page_title="Theo — Restaurant Host", page_icon="🍽️", layout="centered")
st.markdown("""
<style>
    .block-container { max-width: 720px; padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

st.title("🍽️ Theo — Your Restaurant Host")
st.caption("Ask about the menu, opening hours, or make a reservation.")

init_db()
app = build_agent()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Good evening — the kitchen's in full swing and there's a great energy in here tonight. What can I do for you?"}
    ]
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask Theo anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Theo is thinking..."):
            reply = chat(app, prompt, session_id=st.session_state.session_id)
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})

with st.sidebar:
    st.markdown("### About Theo")
    st.markdown("Theo is your restaurant host. Ask him about the menu, hours, or reservations.")
    st.divider()
    st.markdown("**Tools**")
    st.markdown("- 🍴 Menu & prices\n- 🕐 Opening hours\n- 📅 Make reservation\n- 🔍 Check reservation\n- ❌ Cancel reservation")
    st.divider()
    if st.button("🔄 New conversation"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Good evening — the kitchen's in full swing and there's a great energy in here tonight. What can I do for you?"}
        ]
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
