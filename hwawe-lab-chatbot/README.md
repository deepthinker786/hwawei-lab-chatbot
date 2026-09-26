# 🧪 Hwawe Lab Chatbot

A private, local generative-AI chat app with a glass-on-aurora interface.
Built with **Streamlit** + **Ollama** (no cloud API keys, no Gemini), managed with **uv**.

## Features
- Streaming answers with Markdown and code blocks
- Pick any model you have installed in Ollama, live from the sidebar
- Creativity (temperature) slider and editable assistant instructions
- One-click suggestions, new chat, and download chat as `.md`
- Live "Ollama connected" status and clear error messages
- Configuration through `.env`

## Requirements
- [uv](https://docs.astral.sh/uv/) — install: `pip install uv` or see the uv docs
- [Ollama](https://ollama.com/download)
- Python 3.10+ (uv can install it for you)

## Quick start
```bash
# 1. Get a model (one time)
ollama pull llama3.2

# 2. Install dependencies
uv sync

# 3. Configure
cp .env.example .env        # Windows: copy .env.example .env

# 4. Run
uv run streamlit run app.py
```
Open http://localhost:8501. Make sure Ollama is running (`ollama serve`, or the desktop app).

## Configuration (`.env`)
| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Where Ollama is running |
| `OLLAMA_MODEL` | `llama3.2` | Model selected on start |
| `APP_NAME` | `Hwawe Lab` | Name shown in the UI |
| `SYSTEM_PROMPT` | Hwawe AI research assistant | Default assistant instructions |
| `OLLAMA_API_KEY` | empty | Only if your server needs a bearer token |

## Project structure
```
hwawe-lab-chatbot/
├── app.py              # Streamlit app + Ollama streaming
├── assets/style.css    # Theme: aurora background, glass bubbles
├── .streamlit/config.toml
├── pyproject.toml      # uv project + dependencies
├── .env.example        # copy to .env (never commit .env)
└── README.md
```

## Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: Hwawe Lab chatbot"
git branch -M main
# create an empty repo on github.com first, then:
git remote add origin https://github.com/<your-username>/hwawe-lab-chatbot.git
git push -u origin main
```
`.env` is in `.gitignore`, so your settings stay private. Commit `uv.lock` (created by `uv sync`) for reproducible installs.

## Troubleshooting
- **"Ollama not reachable"** — start it with `ollama serve` and check `OLLAMA_HOST`.
- **"Model not found"** — run `ollama pull <model>`, then refresh the page.
- **Slow replies** — try a smaller model such as `llama3.2:1b` or `qwen2.5:1.5b`.
- **Docker/WSL** — set `OLLAMA_HOST` to the host's address, e.g. `http://host.docker.internal:11434`.
