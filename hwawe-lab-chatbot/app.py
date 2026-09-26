"""Hwawe Lab - a private, local generative AI chatbot (Streamlit + Ollama)."""

import os
from datetime import datetime
from pathlib import Path

import ollama
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
APP_NAME = os.getenv("APP_NAME", "Hwawe Lab")
DEFAULT_SYSTEM = os.getenv(
    "SYSTEM_PROMPT",
    "You are Hwawe AI, the research assistant of Hwawe Lab. Answer clearly and "
    "accurately, use Markdown when it helps, and say so when you are not sure.",
)

SUGGESTIONS = [
    ("Explain a concept", "Explain how transformers work in simple terms, with an analogy."),
    ("Write code", "Write a Python function that removes duplicates from a list and keeps the order."),
    ("Plan an experiment", "Help me design a small experiment to compare two machine learning models."),
    ("Summarise & improve", "Give me a checklist for writing a clear, well-structured research summary."),
]

st.set_page_config(
    page_title=f"{APP_NAME} | AI Chat",
    page_icon="🧪",
    layout="centered",
    initial_sidebar_state="expanded",
)

css = Path(__file__).parent / "assets" / "style.css"
st.markdown(f"<style>{css.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


# ---------- Ollama helpers ----------
@st.cache_resource
def get_client() -> ollama.Client:
    headers = {"Authorization": f"Bearer {OLLAMA_API_KEY}"} if OLLAMA_API_KEY else None
    return ollama.Client(host=OLLAMA_HOST, headers=headers)


def list_models() -> list[str] | None:
    """Return installed model names, or None if the Ollama server is unreachable."""
    try:
        response = get_client().list()
        return sorted(m.get("model") or m.get("name") for m in response["models"])
    except Exception:
        return None


def stream_reply(model: str, system: str, history: list[dict], temperature: float):
    payload = [{"role": "system", "content": system}, *history]
    for chunk in get_client().chat(
        model=model, messages=payload, stream=True, options={"temperature": temperature}
    ):
        yield chunk["message"]["content"]


def export_markdown(messages: list[dict], model: str) -> str:
    lines = [f"# {APP_NAME} chat", f"_Model: {model} - {datetime.now():%Y-%m-%d %H:%M}_", ""]
    for m in messages:
        who = "You" if m["role"] == "user" else "Hwawe AI"
        lines += [f"**{who}:**", "", m["content"], ""]
    return "\n".join(lines)


# ---------- State ----------
st.session_state.setdefault("messages", [])
st.session_state.setdefault("pending", None)

# ---------- Sidebar ----------
models = list_models()
online = models is not None

with st.sidebar:
    st.markdown(
        f"""
        <div class="brand">
          <div class="brand-mark">🧪</div>
          <div><div class="brand-name">{APP_NAME}</div>
          <div class="brand-sub">Local AI workspace</div></div>
        </div>
        <div class="status {'on' if online else 'off'}">
          <span class="dot"></span>{'Ollama connected' if online else 'Ollama not reachable'}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if models:
        index = models.index(DEFAULT_MODEL) if DEFAULT_MODEL in models else 0
        model = st.selectbox("Model", models, index=index)
    else:
        model = st.text_input("Model", value=DEFAULT_MODEL, help="Type a model name you have pulled.")

    temperature = st.slider("Creativity", 0.0, 1.5, 0.7, 0.1, help="Lower is focused, higher is more creative.")

    with st.expander("Assistant instructions"):
        system_prompt = st.text_area("System prompt", DEFAULT_SYSTEM, height=140, label_visibility="collapsed")

    st.divider()
    if st.button("New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    if st.session_state.messages:
        st.download_button(
            "Download chat (.md)",
            export_markdown(st.session_state.messages, model),
            file_name=f"hwawe-chat-{datetime.now():%Y%m%d-%H%M}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    st.caption(f"{len(st.session_state.messages)} messages · runs 100% on your machine")

# ---------- Input ----------
typed = st.chat_input(f"Message {APP_NAME} AI...")
prompt = st.session_state.pending or typed
st.session_state.pending = None
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

# ---------- Hero (empty state) ----------
if not st.session_state.messages:
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-badge">✨ Private · Local · Open models</div>
          <h1>What are we working on in {APP_NAME} today?</h1>
          <p>Ask a question, draft code, or think through an idea. Everything runs on your own machine through Ollama.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, (title, text) in enumerate(SUGGESTIONS):
        if cols[i % 2].button(title, key=f"s{i}", help=text, use_container_width=True):
            st.session_state.pending = text
            st.rerun()

# ---------- Conversation ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🧪"):
        st.markdown(msg["content"])

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar="🧪"):
        try:
            reply = st.write_stream(
                stream_reply(model, system_prompt, st.session_state.messages, temperature)
            )
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except ollama.ResponseError as e:
            st.error(f"Ollama error: {e.error}")
            if e.status_code == 404:
                st.info(f"Model not found. Run `ollama pull {model}` in a terminal, then try again.")
        except Exception:
            st.error(f"Can't reach Ollama at {OLLAMA_HOST}. Start it with `ollama serve` and try again.")
