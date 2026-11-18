"""Streamlit chat UI for the retail knowledge base RAG assistant.

Same bring-your-own-key pattern as the companion agentic-AI project: each
visitor pastes their own Anthropic API key into the sidebar, so hosting
this costs the deployer nothing.
"""
import os

import streamlit as st

from rag_core import answer_question, ensure_knowledge_base_built

st.set_page_config(page_title="Retail Knowledge Base Assistant", page_icon="📚", layout="centered")

with st.spinner("Setting up knowledge base (first run only)..."):
    ensure_knowledge_base_built()


def _local_default_key() -> str:
    """Pre-fill the sidebar field from env/secrets for local dev convenience only."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"]
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except (FileNotFoundError, KeyError, st.errors.StreamlitSecretNotFoundError):
        return ""


st.title("📚 Retail Knowledge Base Assistant")
st.caption(
    "Ask about retail operations concepts, store performance, or forecasting "
    "methodology, e.g. \"Why was Random Forest chosen over Extra Trees?\" or "
    "\"How does Store 20 perform during holidays?\""
)

with st.sidebar:
    st.header("Your Anthropic API key")
    api_key = st.text_input(
        "API key",
        value=_local_default_key(),
        type="password",
        placeholder="sk-ant-...",
        help="Get one at console.anthropic.com. Used only for your requests in this "
        "browser session — never stored or logged.",
        label_visibility="collapsed",
    )
    st.caption(
        "This app doesn't ship with a shared key, so each visitor uses their own. "
        "Get a key at [console.anthropic.com](https://console.anthropic.com)."
    )

if not api_key:
    st.info(
        "👈 Paste your Anthropic API key in the sidebar to start chatting. "
        "Don't have one? Create one at "
        "[console.anthropic.com](https://console.anthropic.com).",
        icon="🔑",
    )
    st.stop()

if "chat_turns" not in st.session_state:
    st.session_state.chat_turns = []  # [{role, content, retrieved}]


def render_text(text: str):
    # Escape bare "$" so Streamlit's markdown renderer doesn't treat a pair of
    # dollar amounts as a LaTeX math block.
    st.markdown(text.replace("$", "\\$"))


def render_sources(retrieved):
    with st.expander(f"📚 {len(retrieved)} source(s) retrieved", expanded=False):
        for chunk in retrieved:
            st.markdown(f"**{chunk.source}** — _{chunk.section}_ (distance: {chunk.distance:.3f})")
            st.text(chunk.text)
            st.divider()


for turn in st.session_state.chat_turns:
    with st.chat_message(turn["role"]):
        if turn.get("retrieved"):
            render_sources(turn["retrieved"])
        render_text(turn["content"])

if prompt := st.chat_input("Ask about retail operations..."):
    st.session_state.chat_turns.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        render_text(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching the knowledge base..."):
            try:
                result = answer_question(prompt, api_key=api_key)
            except Exception as exc:
                st.error(f"Error: {exc}")
                st.stop()

        render_sources(result.retrieved)
        render_text(result.answer)

    st.session_state.chat_turns.append(
        {"role": "assistant", "content": result.answer, "retrieved": result.retrieved}
    )

with st.sidebar:
    st.header("About")
    st.write(
        "This assistant answers questions by retrieving relevant excerpts from "
        "a knowledge base — retail-operations glossaries and policy references, "
        "plus data-driven store performance profiles — then asking Claude to "
        "answer grounded only in those excerpts, with sources shown for every "
        "answer."
    )
    if st.button("Clear conversation"):
        st.session_state.chat_turns = []
        st.rerun()
