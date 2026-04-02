<div align="center">

<img src="assets/logo-ver2.png" alt="DeepTutor" width="140" style="border-radius: 15px;">

# DeepTutor: Towards Agentic Personalized Tutoring

[![Python 3.11](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)](LICENSE)

<p>
  <a href="https://discord.gg/eRsjPgMU4t"><img src="https://img.shields.io/badge/Discord-Community-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
  &nbsp;
  <a href="./Communication.md"><img src="https://img.shields.io/badge/Feishu-Group-00D4AA?style=for-the-badge&logo=feishu&logoColor=white" alt="Feishu"></a>
  &nbsp;
  <a href="https://github.com/HKUDS/DeepTutor/issues/78"><img src="https://img.shields.io/badge/WeChat-Group-07C160?style=for-the-badge&logo=wechat&logoColor=white" alt="WeChat"></a>
</p>

[Features](#-features) · [Get Started](#-get-started) · [Explore](#-explore-deeptutor) · [Community](#-community--ecosystem)

[🇨🇳 中文](assets/README/README_CN.md) · [🇯🇵 日本語](assets/README/README_JA.md) · [🇪🇸 Español](assets/README/README_ES.md) · [🇫🇷 Français](assets/README/README_FR.md) · [🇸🇦 العربية](assets/README/README_AR.md) · [🇷🇺 Русский](assets/README/README_RU.md) · [🇮🇳 हिन्दी](assets/README/README_HI.md) · [🇵🇹 Português](assets/README/README_PT.md)

</div>

---
### 📰 News

> **[2026.3.24]** Long time no see! ✨ DeepTutor v1.0.0 is finally here — an agent-native evolution featuring a lightweight refactor, TutorBot, and flexible mode switching under the Apache-2.0 license. A new chapter begins, and our story continues! 

> **[2026.2.6]** 🚀 We've reached 10k stars in just 39 days! A huge thank you to our incredible community for the support! 

> **[2026.1.1]** Happy New Year! Join our [Discord](https://discord.gg/eRsjPgMU4t), [WeChat](https://github.com/HKUDS/DeepTutor/issues/78), or [Discussions](https://github.com/HKUDS/DeepTutor/discussions) — let's shape the future of DeepTutor together!

> **[2025.12.29]** DeepTutor is officially released!

### 📦 Releases

> **[2026.3.24]** [v1.0.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0) — Agent-native refactor with flexible tool integration, CLI & SDK entry points, TutorBot powered by the nanobot engine, Co-Writer, Guided Learning, and persistent memory. DeepTutor is now lighter, faster, and better than ever!

<details>
<summary><b>Past releases</b></summary>

> **[2026.1.23]** [v0.6.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.6.0) — Session persistence, incremental document upload, flexible RAG pipeline import, and full Chinese localization.

> **[2026.1.18]** [v0.5.2](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.2) — Docling support for RAG-Anything, logging system optimization, and bug fixes.

> **[2026.1.15]** [v0.5.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.0) — Unified service configuration, RAG pipeline selection per knowledge base, question generation overhaul, and sidebar customization.

> **[2026.1.9]** [v0.4.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.4.0) — Multi-provider LLM & embedding support, new home page, RAG module decoupling, and environment variable refactor.

> **[2026.1.5]** [v0.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.3.0) — Unified PromptManager architecture, GitHub Actions CI/CD, and pre-built Docker images on GHCR.

> **[2026.1.2]** [v0.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.2.0) — Docker deployment, Next.js 16 & React 19 upgrade, WebSocket security hardening, and critical vulnerability fixes.

</details>

## ✨ Key Features

- **Unified Chat Workspace** — Five powerful modes (Chat, Deep Solve, Quiz Generation, Deep Research, Math Animator) sharing the same context. Switch freely, as you wish.
- **Personal TutorBots** — Autonomous AI tutors with their own workspace, memory, and personality. They set reminders, learn new skills, and grow alongside you.
- **AI Co-Writer** — A Markdown editor with AI deeply woven in. Rewrite, expand, summarize — with full access to your knowledge base and the web.
- **Guided Learning** — Multi-step visual learning plans built from your own materials. Each step becomes an interactive page you can explore and discuss.
- **Knowledge Hub** — Upload documents, build knowledge bases, organize notebooks. Your personal learning infrastructure, always at your fingertips.
- **Persistent Memory** — DeepTutor remembers your learning journey — progress, preferences, and goals. The more you use it, the better it understands you.

---

## 🚀 Get Started

### Option A — Local Install

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor

# Create environment
conda create -n deeptutor python=3.11 && conda activate deeptutor
# Or: python -m venv venv && source venv/bin/activate

# Install core + web
pip install -e ".[server]"
```

Run the **Setup Tour** — a single command that handles everything from configuration to launch:

```bash
python scripts/start_tour.py
```

The tour begins by asking how you'd like to use DeepTutor:

- **Web mode** (recommended) — Configures ports and dependencies, then spins up a temporary server and opens the **Settings** page in your browser. A four-step guided tour walks you through LLM, Embedding, and Search provider setup with live connection testing. Once complete, DeepTutor restarts automatically with your configuration.
- **CLI mode** — A fully interactive terminal flow: choose a dependency profile, configure ports, set up providers, verify connections, and apply — all without leaving the shell.

Either way, you end up with a running DeepTutor at [http://localhost:3782](http://localhost:3782).

<details>
<summary><b>Start services separately</b></summary>

```bash
# Backend (FastAPI)
python -m deeptutor.api.run_server

# Frontend (Next.js)
cd web && npm install && npm run dev -- -p 3782
```

| Service | Port |
|:---:|:---:|
| Backend | `8001` |
| Frontend | `3782` |

</details>

### Option B — Docker Deployment

Docker wraps the backend and frontend into a single container via supervisord — no local Python or Node.js required.

**1. Configure environment variables**

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
cp .env.example .env
```

Edit `.env` and fill in at least the required fields:

```dotenv
# LLM (Required)
LLM_BINDING=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-xxx
LLM_HOST=https://api.openai.com/v1

# Embedding (Required for Knowledge Base)
EMBEDDING_BINDING=openai
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_API_KEY=sk-xxx
EMBEDDING_HOST=https://api.openai.com/v1
EMBEDDING_DIMENSION=3072
```

**2. Build & start**

```bash
docker compose up -d
```

That's it. Open [http://localhost:3782](http://localhost:3782) once the container is healthy.

**3. View logs & stop**

```bash
docker compose logs -f   # tail logs
docker compose down       # stop and remove container
```

<details>
<summary><b>Cloud / remote server deployment</b></summary>

When deploying to a remote server, the browser needs to know the public URL of the backend API. Add one more variable to your `.env`:

```dotenv
# Set to the public URL where the backend is reachable
NEXT_PUBLIC_API_BASE_EXTERNAL=https://your-server.com:8001
```

The frontend startup script applies this value at runtime — no rebuild needed.

</details>

<details>
<summary><b>Development mode (hot-reload)</b></summary>

Layer the dev override to mount source code and enable hot-reload for both services:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Changes to `deeptutor/`, `deeptutor_cli/`, `scripts/`, and `web/` are reflected immediately.

</details>

<details>
<summary><b>Custom ports</b></summary>

Override the default ports in `.env`:

```dotenv
BACKEND_PORT=9001
FRONTEND_PORT=4000
```

Then restart:

```bash
docker compose up -d
```

</details>

<details>
<summary><b>Data persistence</b></summary>

User data and knowledge bases are persisted via Docker volumes mapped to local directories:

| Container path | Host path | Content |
|:---|:---|:---|
| `/app/data/user` | `./data/user` | Settings, memory, workspace, sessions, logs |
| `/app/data/knowledge_bases` | `./data/knowledge_bases` | Uploaded documents & vector indices |

These directories survive `docker compose down` and are reused on the next `docker compose up`.

</details>

<details>
<summary><b>Environment variables reference</b></summary>

| Variable | Required | Description |
|:---|:---:|:---|
| `LLM_BINDING` | **Yes** | LLM provider (`openai`, `anthropic`, etc.) |
| `LLM_MODEL` | **Yes** | Model name (e.g. `gpt-4o`) |
| `LLM_API_KEY` | **Yes** | Your LLM API key |
| `LLM_HOST` | **Yes** | API endpoint URL |
| `EMBEDDING_BINDING` | **Yes** | Embedding provider |
| `EMBEDDING_MODEL` | **Yes** | Embedding model name |
| `EMBEDDING_API_KEY` | **Yes** | Embedding API key |
| `EMBEDDING_HOST` | **Yes** | Embedding endpoint |
| `EMBEDDING_DIMENSION` | **Yes** | Vector dimension |
| `SEARCH_PROVIDER` | No | Search provider (`tavily`, `jina`, `serper`, `perplexity`, etc.) |
| `SEARCH_API_KEY` | No | Search API key |
| `BACKEND_PORT` | No | Backend port (default `8001`) |
| `FRONTEND_PORT` | No | Frontend port (default `3782`) |
| `NEXT_PUBLIC_API_BASE_EXTERNAL` | No | Public backend URL for cloud deployment |
| `DISABLE_SSL_VERIFY` | No | Disable SSL verification (default `false`) |

</details>

### CLI — Agent-Native Interface

DeepTutor exposes a lightweight CLI that doubles as an **agent-native skill interface**. Every capability, knowledge base, memory, and session is accessible through structured commands — which means your AI agents can use DeepTutor too.

Hand the [`SKILL.md`](SKILL.md) at the project root to your agent ([nanobot](https://github.com/HKUDS/nanobot), Openclaw, Zeroclaw, or any tool-using LLM), and it will know how to configure and operate DeepTutor on your behalf.

```bash
deeptutor chat                                   # Interactive REPL
deeptutor run chat "Explain Fourier transform"   # One-shot capability
deeptutor run deep_solve "Solve x^2 = 4"         # Multi-agent problem solving
deeptutor kb create my-kb --doc textbook.pdf     # Build a knowledge base
deeptutor serve --port 8001                      # Start API server
```

<details>
<summary><b>Full CLI command reference</b></summary>

**Top-level**

| Command | Description |
|:---|:---|
| `deeptutor run <capability> <message>` | Run any capability in a single turn (`chat`, `deep_solve`, `deep_question`, `deep_research`, `math_animator`) |
| `deeptutor serve` | Start the DeepTutor API server |

**`deeptutor chat`**

| Command | Description |
|:---|:---|
| `deeptutor chat` | Interactive REPL with optional `--capability`, `--tool`, `--kb`, `--language` |

**`deeptutor bot`**

| Command | Description |
|:---|:---|
| `deeptutor bot list` | List all TutorBot instances |
| `deeptutor bot create <id>` | Create and start a new bot (`--name`, `--persona`, `--model`) |
| `deeptutor bot start <id>` | Start a bot |
| `deeptutor bot stop <id>` | Stop a bot |

**`deeptutor kb`**

| Command | Description |
|:---|:---|
| `deeptutor kb list` | List all knowledge bases |
| `deeptutor kb info <name>` | Show knowledge base details |
| `deeptutor kb create <name>` | Create from documents (`--doc`, `--docs-dir`) |
| `deeptutor kb add <name>` | Add documents incrementally |
| `deeptutor kb search <name> <query>` | Search a knowledge base |
| `deeptutor kb set-default <name>` | Set as default KB |
| `deeptutor kb delete <name>` | Delete a knowledge base (`--force`) |

**`deeptutor memory`**

| Command | Description |
|:---|:---|
| `deeptutor memory show [file]` | View memory (`summary`, `profile`, or `all`) |
| `deeptutor memory clear [file]` | Clear memory (`--force`) |

**`deeptutor session`**

| Command | Description |
|:---|:---|
| `deeptutor session list` | List sessions (`--limit`) |
| `deeptutor session show <id>` | View session messages |
| `deeptutor session open <id>` | Resume session in REPL |
| `deeptutor session rename <id>` | Rename a session (`--title`) |
| `deeptutor session delete <id>` | Delete a session |

**`deeptutor notebook`**

| Command | Description |
|:---|:---|
| `deeptutor notebook list` | List notebooks |
| `deeptutor notebook create <name>` | Create a notebook (`--description`) |
| `deeptutor notebook show <id>` | View notebook records |
| `deeptutor notebook add-md <id> <path>` | Import markdown as record |
| `deeptutor notebook replace-md <id> <rec> <path>` | Replace a markdown record |
| `deeptutor notebook remove-record <id> <rec>` | Remove a record |

**`deeptutor config` / `plugin` / `provider`**

| Command | Description |
|:---|:---|
| `deeptutor config show` | Print current configuration summary |
| `deeptutor plugin list` | List registered tools and capabilities |
| `deeptutor plugin info <name>` | Show tool or capability details |
| `deeptutor provider login <provider>` | OAuth login (`openai-codex`, `github-copilot`) |

</details>

---

## 📖 Explore DeepTutor

### 💬 Chat — Unified Intelligent Workspace

Five distinct modes coexist in a single workspace, bound by a **unified context management system**. Conversation history, knowledge bases, and references persist across modes — switch between them freely within the same topic, whenever the moment calls for it.

| Mode | What It Does |
|:---|:---|
| **Chat** | Fluid, tool-augmented conversation. Choose from RAG retrieval, web search, code execution, deep reasoning, brainstorming, and paper search — mix and match as needed. |
| **Deep Solve** | Multi-agent problem solving: plan, investigate, solve, and verify — with precise source citations at every step. |
| **Quiz Generation** | Generate assessments grounded in your knowledge base, with built-in validation. |
| **Deep Research** | Decompose a topic into subtopics, dispatch parallel research agents across RAG, web, and academic papers, and produce a fully cited report. |
| **Math Animator** | Turn mathematical concepts into visual animations and storyboards powered by Manim. |

Tools are **decoupled from workflows** — in every mode, you decide which tools to enable, how many to use, or whether to use any at all. The workflow orchestrates the reasoning; the tools are yours to compose.

> Start with a quick chat question, escalate to Deep Solve when it gets hard, generate quiz questions to test yourself, then launch a Deep Research to go deeper — all in one continuous thread.

### 🦞 TutorBot — Your Personal AI Tutor

TutorBot is not a chatbot. It is a persistent, autonomous tutor built on [nanobot](https://github.com/HKUDS/nanobot) — a lightweight agent engine that gives each instance its own independent agent loop.

Every TutorBot lives in its own **workspace** with its own **memory** and **skill set**, while staying connected to DeepTutor's shared memory layer. Think of it as a real tutor who remembers everything and keeps getting better.

- **Custom Soul** — Shape your tutor's personality, tone, and values through editable Soul templates. Socratic, encouraging, rigorous — you decide.
- **Independent Memory** — Each bot maintains its own workspace and conversation history, separate from other bots, yet connected to DeepTutor's global memory.
- **Reminders & Scheduling** — Set up recurring study check-ins, review reminders, and periodic tasks through the built-in heartbeat system.
- **DeepTutor Integration** — Bots can call into DeepTutor's full capabilities: search your knowledge bases, execute code, browse the web, and more.
- **Skill Learning** — Teach your bot new abilities by adding skill files to its workspace. It learns as you expand its reach.

### ✍️ Co-Writer — AI Inside Your Editor

Co-Writer brings the intelligence of Chat directly into a writing surface. It is a full-featured Markdown editor where AI is a first-class collaborator — not a sidebar, not an afterthought.

Select any text and choose **Rewrite**, **Expand**, or **Shorten** — optionally drawing context from your knowledge base or the web. The editing flow is non-destructive with full undo/redo, and every piece you write can be saved straight to your notebooks, feeding back into your learning ecosystem.

### 🎓 Guided Learning — Visual, Step-by-Step Mastery

Guided Learning turns your personal materials into structured, multi-step learning journeys. Provide a topic, optionally link notebook records, and DeepTutor will:

1. **Design a learning plan** — Identify 3–5 progressive knowledge points from your materials.
2. **Generate interactive pages** — Each point becomes a rich visual HTML page with explanations, diagrams, and examples.
3. **Enable contextual Q&A** — Chat alongside each step for deeper exploration.
4. **Summarize your progress** — Upon completion, receive a learning summary of everything you've covered.

Sessions are persistent — pause, resume, or revisit any step at any time.

### 📚 Knowledge Management — Your Learning Infrastructure

Knowledge is where you build and manage the document collections that power everything else in DeepTutor.

- **Knowledge Bases** — Upload PDF, TXT, or Markdown files to create searchable, RAG-ready collections. Add documents incrementally as your library grows.
- **Notebooks** — Organize learning records across sessions. Save insights from Chat, Guided Learning, Co-Writer, or Deep Research into categorized, color-coded notebooks.

Your knowledge base is not passive storage — it actively participates in every conversation, every research session, and every learning path you create.

### 🧠 Memory — DeepTutor Learns As You Learn

DeepTutor maintains a persistent, evolving understanding of you through two complementary dimensions:

- **Summary** — A running digest of your learning progress: what you've studied, which topics you've explored, and how your understanding has developed.
- **Profile** — Your learner identity: preferences, knowledge level, goals, and communication style — automatically refined through every interaction.

Memory is shared across all features and all your TutorBots. The more you use DeepTutor, the more personalized and effective it becomes.

## 🌐 Community & Ecosystem

DeepTutor stands on the shoulders of outstanding open-source projects:

| Project | Role in DeepTutor |
|:---|:---|
| [**nanobot**](https://github.com/HKUDS/nanobot) | Ultra-lightweight agent engine powering TutorBot |
| [**LlamaIndex**](https://github.com/run-llama/llama_index) | RAG pipeline and document indexing backbone |
| [**ManimCat**](https://github.com/Wing900/ManimCat) | AI-driven math animation generation for Math Animator |

**From the HKUDS ecosystem:**

| [⚡ LightRAG](https://github.com/HKUDS/LightRAG) | [🤖 AutoAgent](https://github.com/HKUDS/AutoAgent) | [🔬 AI-Researcher](https://github.com/HKUDS/AI-Researcher) | [🧬 nanobot](https://github.com/HKUDS/nanobot) |
|:---:|:---:|:---:|:---:|
| Simple & Fast RAG | Zero-Code Agent Framework | Automated Research | Ultra-Lightweight AI Agent |


## 🤝 Contributing

<div align="center">

We hope DeepTutor becomes a gift for the community. 🎁

<a href="https://github.com/HKUDS/DeepTutor/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HKUDS/DeepTutor&max=999" alt="Contributors" />
</a>

</div>

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on setting up your development environment, code standards, and pull request workflow.

## ⭐ Star History

<div align="center">

<a href="https://www.star-history.com/#HKUDS/DeepTutor&type=timeline&legend=top-left">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&legend=top-left" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&legend=top-left" />
  </picture>
</a>

</div>

<div align="center">

**[Data Intelligence Lab @ HKU](https://github.com/HKUDS)**

[⭐ Star us](https://github.com/HKUDS/DeepTutor/stargazers) · [🐛 Report a bug](https://github.com/HKUDS/DeepTutor/issues) · [💬 Discussions](https://github.com/HKUDS/DeepTutor/discussions)

---

Licensed under the [Apache License 2.0](LICENSE).

<p>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.DeepTutor&style=for-the-badge&color=00d4ff" alt="Views">
</p>

</div>
