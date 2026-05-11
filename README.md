<div align="center">

<img src="assets/logo-ver2.png" alt="DeepTutor" width="140" style="border-radius: 15px;">

# DeepTutor: Agent-Native Personalized Tutoring

<a href="https://trendshift.io/repositories/17099" target="_blank"><img src="https://trendshift.io/api/badge/repositories/17099" alt="HKUDS%2FDeepTutor | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/HKUDS/DeepTutor?style=flat-square&color=brightgreen)](https://github.com/HKUDS/DeepTutor/releases)
[![arXiv](https://img.shields.io/badge/arXiv-2604.26962-b31b1b?style=flat-square&logo=arxiv&logoColor=white)](https://arxiv.org/abs/2604.26962)

[![Discord](https://img.shields.io/badge/Discord-Community-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.gg/eRsjPgMU4t)
[![Feishu](https://img.shields.io/badge/Feishu-Group-00D4AA?style=flat-square&logo=feishu&logoColor=white)](./Communication.md)
[![WeChat](https://img.shields.io/badge/WeChat-Group-07C160?style=flat-square&logo=wechat&logoColor=white)](https://github.com/HKUDS/DeepTutor/issues/78)

[Features](#-key-features) · [Get Started](#-get-started) · [Explore](#-explore-deeptutor) · [TutorBot](#-tutorbot--persistent-autonomous-ai-tutors) · [CLI](#%EF%B8%8F-deeptutor-cli--agent-native-interface) · [Multi-User](#-multi-user--shared-deployments-with-per-user-workspaces) · [Roadmap](#%EF%B8%8F-roadmap) · [Community](#-community--ecosystem)

[🇨🇳 中文](assets/README/README_CN.md) · [🇯🇵 日本語](assets/README/README_JA.md) · [🇪🇸 Español](assets/README/README_ES.md) · [🇫🇷 Français](assets/README/README_FR.md) · [🇸🇦 العربية](assets/README/README_AR.md) · [🇷🇺 Русский](assets/README/README_RU.md) · [🇮🇳 हिन्दी](assets/README/README_HI.md) · [🇵🇹 Português](assets/README/README_PT.md) · [🇹🇭 ภาษาไทย](assets/README/README_TH.md)  · 🇵🇱 [Polski](assets/README/README_PL.md)

</div>

---

> 🤝 **We welcome any kinds of contributing!** See our [Contributing Guide](CONTRIBUTING.md) for branching strategy, coding standards, and how to get started.

### 📦 Releases

> **[2026.5.10]** [v1.3.10](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.10) — Remote Docker CORS recovery, `DISABLE_SSL_VERIFY` across SDK providers, safer code-block citations, and optional Matrix E2EE add-on.

> **[2026.5.9]** [v1.3.9](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.9) — TutorBot Zulip and NVIDIA NIM support, safer thinking-model routing, `deeptutor start`, sidebar tooltips, and session-store parity.

> **[2026.5.8]** [v1.3.8](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.8) — Optional multi-user deployments with isolated user workspaces, admin grants, auth routes, and scoped runtime access.

> **[2026.5.4]** [v1.3.7](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.7) — Thinking-model/provider fixes, visible Knowledge index history, and safer Co-Writer clear/template editing.

> **[2026.5.3]** [v1.3.6](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.6) — Catalog-based model selection for chat and TutorBot, safer RAG re-indexing, OpenAI Responses token-limit fixes, and Skills editor validation.

> **[2026.5.2]** [v1.3.5](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.5) — Smoother local launch settings, safer RAG queries, cleaner local embedding auth, and Settings dark-mode polish.

> **[2026.5.1]** [v1.3.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.4) — Book page chat persistence and rebuild flows, chat-to-book references, stronger language/reasoning handling, RAG document extraction hardening.

> **[2026.4.30]** [v1.3.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.3) — NVIDIA NIM + Gemini embedding support, unified Space context for chat history/skills/memory, session snapshots, RAG re-index resilience.

> **[2026.4.29]** [v1.3.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.2) — Transparent embedding endpoint URLs, RAG re-index resilience for invalid persisted vectors, memory cleanup for thinking-model output, Deep Solve runtime fix.

> **[2026.4.28]** [v1.3.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.1) — Stability: safer RAG routing & embedding validation, Docker persistence, IME-safe input, Windows/GBK robustness.

> **[2026.4.27]** [v1.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.3.0) — Versioned KB indexes with re-index workflow, rebuilt Knowledge workspace, embedding auto-discovery with new adapters, Space hub.

<details>
<summary><b>Past releases (more than 2 weeks ago)</b></summary>

> **[2026.4.25]** [v1.2.5](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.5) — Persistent chat attachments with file-preview drawer, attachment-aware capability pipelines, TutorBot Markdown export.

> **[2026.4.25]** [v1.2.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.4) — Text/code/SVG attachments, one-command Setup Tour, Markdown chat export, compact KB management UI.

> **[2026.4.24]** [v1.2.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.3) — Document attachments (PDF/DOCX/XLSX/PPTX), reasoning thinking-block display, Soul template editor, Co-Writer save-to-notebook.

> **[2026.4.22]** [v1.2.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.2) — User-authored Skills system, chat input performance overhaul, TutorBot auto-start, Book Library UI, visualization fullscreen.

> **[2026.4.21]** [v1.2.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.1) — Per-stage token limits, Regenerate response across all entry points, RAG & Gemma compatibility fixes.

> **[2026.4.20]** [v1.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.2.0) — Book Engine "living book" compiler, multi-document Co-Writer, interactive HTML visualizations, Question Bank @-mention.

> **[2026.4.18]** [v1.1.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.2) — Schema-driven Channels tab, RAG single-pipeline consolidation, externalized chat prompts.

> **[2026.4.17]** [v1.1.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.1) — Universal "Answer now", Co-Writer scroll sync, unified settings panel, streaming Stop button.

> **[2026.4.15]** [v1.1.0](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0) — LaTeX block math overhaul, LLM diagnostic probe, Docker + local LLM guidance.

> **[2026.4.14]** [v1.1.0-beta](https://github.com/HKUDS/DeepTutor/releases/tag/v1.1.0-beta) — Bookmarkable sessions, Snow theme, WebSocket heartbeat & auto-reconnect, embedding registry overhaul.

> **[2026.4.13]** [v1.0.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.3) — Question Notebook with bookmarks & categories, Mermaid in Visualize, embedding mismatch detection, Qwen/vLLM compatibility, LM Studio & llama.cpp support, and Glass theme.

> **[2026.4.11]** [v1.0.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.2) — Search consolidation with SearXNG fallback, provider switch fix, and frontend resource leak fixes.

> **[2026.4.10]** [v1.0.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.1) — Visualize capability (Chart.js/SVG), quiz duplicate prevention, and o4-mini model support.

> **[2026.4.10]** [v1.0.0-beta.4](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.4) — Embedding progress tracking with rate-limit retry, cross-platform dependency fixes, and MIME validation fix.

> **[2026.4.8]** [v1.0.0-beta.3](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.3) — Native OpenAI/Anthropic SDK (drop litellm), Windows Math Animator support, robust JSON parsing, and full Chinese i18n.

> **[2026.4.7]** [v1.0.0-beta.2](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.2) — Hot settings reload, MinerU nested output, WebSocket fix, and Python 3.11+ minimum.

> **[2026.4.4]** [v1.0.0-beta.1](https://github.com/HKUDS/DeepTutor/releases/tag/v1.0.0-beta.1) — Agent-native architecture rewrite (~200k lines): Tools + Capabilities plugin model, CLI & SDK, TutorBot, Co-Writer, Guided Learning, and persistent memory.

> **[2026.1.23]** [v0.6.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.6.0) — Session persistence, incremental document upload, flexible RAG pipeline import, and full Chinese localization.

> **[2026.1.18]** [v0.5.2](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.2) — Docling support for RAG-Anything, logging system optimization, and bug fixes.

> **[2026.1.15]** [v0.5.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.0) — Unified service configuration, RAG pipeline selection per knowledge base, question generation overhaul, and sidebar customization.

> **[2026.1.9]** [v0.4.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.4.0) — Multi-provider LLM & embedding support, new home page, RAG module decoupling, and environment variable refactor.

> **[2026.1.5]** [v0.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.3.0) — Unified PromptManager architecture, GitHub Actions CI/CD, and pre-built Docker images on GHCR.

> **[2026.1.2]** [v0.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.2.0) — Docker deployment, Next.js 16 & React 19 upgrade, WebSocket security hardening, and critical vulnerability fixes.

</details>

### 📰 News

> **[2026.4.19]** 🎉 We've reached 20k stars after 111 days! Thank you for the incredible support — we're committed to continuous iteration toward truly personalized, intelligent tutoring for everyone.

> **[2026.4.10]** 📄 Our paper is now live on arXiv! Read the [preprint](https://arxiv.org/abs/2604.26962) to learn more about the design and ideas behind DeepTutor.

> **[2026.4.4]** Long time no see! ✨ DeepTutor v1.0.0 is finally here — an agent-native evolution featuring a ground-up architecture rewrite, TutorBot, and flexible mode switching under the Apache-2.0 license. A new chapter begins, and our story continues!

> **[2026.2.6]** 🚀 We've reached 10k stars in just 39 days! A huge thank you to our incredible community for the support!

> **[2026.1.1]** Happy New Year! Join our [Discord](https://discord.gg/eRsjPgMU4t), [WeChat](https://github.com/HKUDS/DeepTutor/issues/78), or [Discussions](https://github.com/HKUDS/DeepTutor/discussions) — let's shape the future of DeepTutor together!

> **[2025.12.29]** DeepTutor is officially released!


## ✨ Key Features

- **Unified Chat Workspace** — Six modes, one thread. Chat, Deep Solve, Quiz Generation, Deep Research, Math Animator, and Visualize share the same context — start a conversation, escalate to multi-agent problem solving, generate quizzes, visualize concepts, then deep-dive into research, all without losing a single message.
- **AI Co-Writer** — A multi-document Markdown workspace where AI is a first-class collaborator. Select text, rewrite, expand, or summarize — drawing from your knowledge base and the web. Every piece feeds back into your learning ecosystem.
- **Book Engine** — Turn your materials into structured, interactive "living books". A multi-agent pipeline designs outlines, retrieves relevant sources, and compiles rich pages with 13 block types — quizzes, flash cards, timelines, concept graphs, interactive demos, and more.
- **Knowledge Hub** — Upload PDFs, Markdown, and text files to build RAG-ready knowledge bases. Organize insights in color-coded notebooks, revisit quiz questions in the Question Bank, and create custom Skills that shape how DeepTutor teaches you. Your documents don't just sit there — they actively power every conversation.
- **Persistent Memory** — DeepTutor builds a living profile of you: what you've studied, how you learn, and where you're heading. Shared across all features and TutorBots, it gets sharper with every interaction.
- **Personal TutorBots** — Not chatbots — autonomous tutors. Each TutorBot lives in its own workspace with its own memory, personality, and skill set. They set reminders, learn new abilities, and evolve as you grow. Powered by [nanobot](https://github.com/HKUDS/nanobot).
- **Agent-Native CLI** — Every capability, knowledge base, session, and TutorBot is one command away. Rich terminal output for humans, structured JSON for AI agents and pipelines. Hand DeepTutor a [`SKILL.md`](SKILL.md) and your agents can operate it autonomously.
- **Optional Authentication** — Disabled by default for local use. Set `data/user/settings/auth.json` to require login when hosting publicly. Multi-user support with bcrypt-hashed passwords, JWT sessions, a self-service registration page, and a built-in admin dashboard for managing accounts and roles. Optionally back auth and storage with **PocketBase** for OAuth-ready authentication and improved multi-user concurrency — drops in as an optional sidecar with no code changes required.

---

## 🚀 Get Started

DeepTutor now has four parallel installation paths. All of them use the same runtime configuration layout:

- Settings live in `data/user/settings/` under your current workspace, or under `DEEPTUTOR_HOME` / `deeptutor start --home` when you choose one explicitly.
- `model_catalog.json` stores model provider profiles, base URLs, API keys, active models, embedding settings, and search settings.
- `system.json` stores launch ports, public API base, CORS, TLS, and attachment options.
- `auth.json` stores the optional auth toggle and bootstrap credential hash.
- `integrations.json` stores optional sidecars such as PocketBase.
- Project-root `.env` is no longer used as an application configuration file.

For the full local app, the recommended order is **choose a workspace → install → `deeptutor init` → `deeptutor start`**. `deeptutor start` can backfill missing default files as a safety net, but normal first-run setup should go through `deeptutor init` so ports and model settings are explicit before the Web app starts.

### Option 1 — Install DeepTutor

Use this when you want the full local Web app and CLI without cloning the repository.

```bash
mkdir -p my-deeptutor
cd my-deeptutor
pip install -U deeptutor
deeptutor init
deeptutor start
```

`deeptutor init` writes configuration under `data/user/settings/` in the directory where you run it. It prompts for:

- Backend port, default `8001`
- Frontend port, default `3782`
- LLM provider binding, base URL, API key, and model name
- Optional embedding provider for Knowledge Base / RAG

After `deeptutor start`, open the frontend URL printed in the terminal. With default ports, that URL is [http://127.0.0.1:3782](http://127.0.0.1:3782). If you changed `frontend_port` during `deeptutor init` or later edited `data/user/settings/system.json`, use that configured port instead.

Keep the `deeptutor start` terminal open. Press `Ctrl+C` in that terminal to stop both backend and frontend.

Notes:

- `deeptutor start` starts the FastAPI backend and the packaged Next.js frontend together.
- The packaged Web app does not require `git clone` or `npm install`, but it still needs a local Node.js 20+ runtime to execute the bundled Next.js standalone server.
- If you deliberately skip `deeptutor init` for a quick trial, the app starts with safe default ports and empty model settings; configure models afterward in **Settings → Models**.

### Option 2 — Install From Source

Use this when you are developing DeepTutor or want to run directly from a checkout.

**1. Clone the repository**

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
```

**2. Create a Python environment**

macOS / Linux with `venv`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Windows PowerShell with `venv`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Conda / Miniconda:

```bash
conda create -n deeptutor python=3.11
conda activate deeptutor
python -m pip install --upgrade pip
```

**3. Install the local package and frontend dependencies**

```bash
pip install -e .
cd web
npm install
cd ..
```

**4. Configure and start**

```bash
deeptutor init
deeptutor start
```

Source installs use the local `web/` directory for the frontend. They are intentionally developer-friendly and do not write configuration to `.env`; edit `data/user/settings/*.json` or use the Web Settings page.

Useful developer extras:

```bash
pip install -e ".[dev]"             # tests/lint tools
pip install -e ".[tutorbot]"        # TutorBot engine + channel SDKs
pip install -e ".[matrix]"          # Matrix channel without E2EE/libolm
pip install -e ".[matrix-e2e]"      # Matrix E2EE; requires libolm
pip install -e ".[math-animator]"   # Manim addon; requires LaTeX/ffmpeg/system libs
```

### Option 3 — Docker

Use this when you want the full Web app in one container. Images are published to GitHub Container Registry:

- `ghcr.io/hkuds/deeptutor:latest` — stable release
- `ghcr.io/hkuds/deeptutor:pre` — pre-release, when available

```bash
docker pull ghcr.io/hkuds/deeptutor:latest
docker run -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

Then open [http://127.0.0.1:3782](http://127.0.0.1:3782). Config, API keys, logs, workspace files, memory, and knowledge bases are stored in the `deeptutor-data` volume under `/app/data`.

The container creates `/app/data/user/settings/*.json` automatically on first boot. You can configure model providers directly in the Web Settings page without preparing local JSON files manually.

To use different host ports, change the left side of the `-p` mappings. For example, `-p 127.0.0.1:8088:3782` makes the Web UI available at `http://127.0.0.1:8088` while the container still listens on `3782`. If you change the container-side ports in `/app/data/user/settings/system.json`, restart the container and make the right side of each `-p host:container` mapping match the configured container port.

#### Connecting To Ollama Or Other Host Services

Inside a Docker container, `localhost` refers to the container itself, not your host machine. If you run Ollama, LM Studio, llama.cpp, vLLM, or another model service on the host, use one of these approaches.

Option A — host gateway, recommended for normal Docker runs:

```bash
docker run -p 127.0.0.1:3782:3782 \
  -p 127.0.0.1:8001:8001 \
  --add-host=host.docker.internal:host-gateway \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

Then in **DeepTutor Settings → Models**, set the provider Base URL to `host.docker.internal`:

- Ollama LLM endpoint: `http://host.docker.internal:11434/v1`
- Ollama embedding endpoint: `http://host.docker.internal:11434/api/embed`
- LM Studio: `http://host.docker.internal:1234/v1`
- llama.cpp: `http://host.docker.internal:8080/v1`

On Docker Desktop for macOS/Windows, `host.docker.internal` is usually available even without `--add-host`. On Linux, the `--add-host=host.docker.internal:host-gateway` flag is the portable way to create that hostname on modern Docker Engine.

Option B — host networking, Linux only:

```bash
docker run --network=host \
  -v deeptutor-data:/app/data \
  ghcr.io/hkuds/deeptutor:latest
```

No `-p` mapping is needed in host-network mode. The container shares the host network directly, so open [http://127.0.0.1:3782](http://127.0.0.1:3782) by default, or the `frontend_port` configured in `/app/data/user/settings/system.json`. In this mode, host services can usually be reached with normal localhost URLs such as `http://127.0.0.1:11434/v1`. Host networking exposes container ports directly on the host and may conflict with existing services.

To stop a foreground Docker run, press `Ctrl+C`. If you started it detached with `-d`, run `docker stop <container-name-or-id>`.

### Option 4 — CLI Only

Use this when you do not need the Web UI.

```bash
pip install -U deeptutor-cli
deeptutor init --cli
deeptutor chat
```

`deeptutor init --cli` uses the same `data/user/settings/` layout as the full app, but changes the wizard behavior:

- It skips backend/frontend port prompts because CLI-only usage does not start the Web app.
- It still writes default `system.json`, `auth.json`, `integrations.json`, `model_catalog.json`, `main.yaml`, and `agents.yaml` so the runtime layout is complete.
- It still prompts for the active LLM provider and model.
- It asks whether to configure embeddings, but the default answer is `No`; choose `Yes` if you plan to use `deeptutor kb ...` or RAG tools.

Common CLI commands:

```bash
deeptutor chat
deeptutor chat --capability deep_solve --tool rag --kb my-kb
deeptutor run chat "Explain Fourier transform"
deeptutor run deep_solve "Solve x^2 = 4" --tool rag --kb my-kb
deeptutor kb create my-kb --doc textbook.pdf
deeptutor kb list
deeptutor memory show
```

`deeptutor-cli` does not ship Web assets or server dependencies. If you later want the Web app, install the full package with `pip install -U deeptutor`, run `deeptutor init` if you want to add Web ports, and then run `deeptutor start` from the same workspace.

### Configuration Reference

The Web Settings page is the recommended editor, but the files are plain JSON/YAML and can be managed directly:

| File | Purpose |
|:---|:---|
| `data/user/settings/model_catalog.json` | LLM, embedding, and search provider profiles; API keys; active models |
| `data/user/settings/system.json` | Backend/frontend ports, public API base, CORS, SSL verification, attachment directory |
| `data/user/settings/auth.json` | Optional auth toggle, username, password hash, token/cookie settings |
| `data/user/settings/integrations.json` | Optional PocketBase and sidecar integration settings |
| `data/user/settings/interface.json` | UI language/theme/sidebar preferences |
| `data/user/settings/main.yaml` | Runtime behavior defaults and path injection |
| `data/user/settings/agents.yaml` | Capability/tool temperature and token settings |

Minimal model setup can be done in the browser: open **Settings → Models**, add an LLM profile, set Base URL / API key / model name, and save. Add an embedding profile only if you plan to use Knowledge Base / RAG features.

## 📖 Explore DeepTutor

<div align="center">
<img src="assets/figs/deeptutor-architecture.png" alt="DeepTutor Architecture" width="800">
</div>

### 💬 Chat — Unified Intelligent Workspace

<div align="center">
<img src="assets/figs/dt-chat.png" alt="Chat Workspace" width="800">
</div>

Six distinct modes coexist in a single workspace, bound by a **unified context management system**. Conversation history, knowledge bases, and references persist across modes — switch between them freely within the same topic, whenever the moment calls for it.

| Mode | What It Does |
|:---|:---|
| **Chat** | Fluid, tool-augmented conversation. Choose from RAG retrieval, web search, code execution, deep reasoning, brainstorming, and paper search — mix and match as needed. |
| **Deep Solve** | Multi-agent problem solving: plan, investigate, solve, and verify — with precise source citations at every step. |
| **Quiz Generation** | Generate assessments grounded in your knowledge base, with built-in validation. |
| **Deep Research** | Decompose a topic into subtopics, dispatch parallel research agents across RAG, web, and academic papers, and produce a fully cited report. |
| **Math Animator** | Turn mathematical concepts into visual animations and storyboards powered by Manim. |
| **Visualize** | Generate interactive SVG diagrams, Chart.js charts, Mermaid graphs, or self-contained HTML pages from natural language descriptions. |

Tools are **decoupled from workflows** — in every mode, you decide which tools to enable, how many to use, or whether to use any at all. The workflow orchestrates the reasoning; the tools are yours to compose.

> Start with a quick chat question, escalate to Deep Solve when it gets hard, visualize a concept, generate quiz questions to test yourself, then launch a Deep Research to go deeper — all in one continuous thread.

### ✍️ Co-Writer — Multi-Document AI Writing Workspace

<div align="center">
<img src="assets/figs/dt-cowriter.png" alt="Co-Writer" width="800">
</div>

Co-Writer brings the intelligence of Chat directly into a writing surface. Create and manage multiple documents, each persisted in its own workspace — not a single throwaway scratchpad, but a full-featured multi-document Markdown editor where AI is a first-class collaborator.

Select any text and choose **Rewrite**, **Expand**, or **Shorten** — optionally drawing context from your knowledge base or the web. The editing flow is non-destructive with full undo/redo, and every piece you write can be saved straight to your notebooks, feeding back into your learning ecosystem.

### 📖 Book Engine — Interactive "Living Books"

<div align="center">
<img src="assets/figs/dt-book-0.png" alt="Book Library" width="270"><img src="assets/figs/dt-book-1.png" alt="Book Reader" width="270"><img src="assets/figs/dt-book-2.png" alt="Book Animation" width="270">
</div>

Give DeepTutor a topic, point it at your knowledge base, and it produces a structured, interactive book — not a static export, but a living document you can read, quiz yourself on, and discuss in context.

Behind the scenes, a multi-agent pipeline handles the heavy lifting: proposing an outline, retrieving relevant sources from your knowledge base, synthesizing a chapter tree, planning each page, and compiling every block. You stay in control — review the proposal, reorder chapters, and chat alongside any page.

Pages are assembled from 13 block types — text, callout, quiz, flash cards, code, figure, deep dive, animation, interactive demo, timeline, concept graph, section, and user note — each rendered with its own interactive component. A real-time progress timeline lets you watch compilation unfold as the book takes shape.

### 📚 Knowledge Management — Your Learning Infrastructure

<div align="center">
<img src="assets/figs/dt-knowledge.png" alt="Knowledge Management" width="800">
</div>

Knowledge is where you build and manage the document collections, notes, and teaching personas that power everything else in DeepTutor.

- **Knowledge Bases** — Upload PDFs, Office files (DOCX/XLSX/PPTX), Markdown, and a wide range of text and code files to create searchable, RAG-ready collections. Add documents incrementally as your library grows.
- **Notebooks** — Organize learning records across sessions. Save insights from Chat, Co-Writer, Book, or Deep Research into categorized, color-coded notebooks.
- **Question Bank** — Browse and revisit all generated quiz questions. Bookmark entries and @-mention them directly in chat to reason over past performance.
- **Skills** — Create custom teaching personas via `SKILL.md` files. Each skill defines a name, description, optional triggers, and a Markdown body that is injected into the chat system prompt when active — turning DeepTutor into a Socratic tutor, a peer study partner, a research assistant, or any role you design.

Your knowledge base is not passive storage — it actively participates in every conversation, every research session, and every learning path you create.

### 🧠 Memory — DeepTutor Learns As You Learn

<div align="center">
<img src="assets/figs/dt-memory.png" alt="Memory" width="800">
</div>

DeepTutor maintains a persistent, evolving understanding of you through two complementary dimensions:

- **Summary** — A running digest of your learning progress: what you've studied, which topics you've explored, and how your understanding has developed.
- **Profile** — Your learner identity: preferences, knowledge level, goals, and communication style — automatically refined through every interaction.

Memory is shared across all features and all your TutorBots. The more you use DeepTutor, the more personalized and effective it becomes.

---

### 🦞 TutorBot — Persistent, Autonomous AI Tutors

<div align="center">
<img src="assets/figs/tutorbot-architecture.png" alt="TutorBot Architecture" width="800">
</div>

TutorBot is not a chatbot — it is a **persistent, multi-instance agent** built on [nanobot](https://github.com/HKUDS/nanobot). Each TutorBot runs its own agent loop with independent workspace, memory, and personality. Create a Socratic math tutor, a patient writing coach, and a rigorous research advisor — all running simultaneously, each evolving with you.

<div align="center">
<img src="assets/figs/tb.png" alt="TutorBot" width="800">
</div>

- **Soul Templates** — Define your tutor's personality, tone, and teaching philosophy through editable Soul files. Choose from built-in archetypes (Socratic, encouraging, rigorous) or craft your own — the soul shapes every response.
- **Independent Workspace** — Each bot has its own directory with separate memory, sessions, skills, and configuration — fully isolated yet able to access DeepTutor's shared knowledge layer.
- **Proactive Heartbeat** — Bots don't just respond — they initiate. The built-in Heartbeat system enables recurring study check-ins, review reminders, and scheduled tasks. Your tutor shows up even when you don't.
- **Full Tool Access** — Every bot reaches into DeepTutor's complete toolkit: RAG retrieval, code execution, web search, academic paper search, deep reasoning, and brainstorming.
- **Skill Learning** — Teach your bot new abilities by adding skill files to its workspace. As your needs evolve, so does your tutor's capability.
- **Multi-Channel Presence** — Connect bots to Telegram, Discord, Slack, Feishu, WeChat Work, DingTalk, Matrix, QQ, WhatsApp, Email, and more. Your tutor meets you wherever you are.
- **Team & Sub-Agents** — Spawn background sub-agents or orchestrate multi-agent teams within a single bot for complex, long-running tasks.

```bash
deeptutor bot create math-tutor --persona "Socratic math teacher who uses probing questions"
deeptutor bot create writing-coach --persona "Patient, detail-oriented writing mentor"
deeptutor bot list                  # See all your active tutors
```

---

### ⌨️ DeepTutor CLI — Agent-Native Interface

<div align="center">
<img src="assets/figs/cli-architecture.png" alt="DeepTutor CLI Architecture" width="800">
</div>

DeepTutor is fully CLI-native. Every capability, knowledge base, session, memory, and TutorBot is one command away — no browser required. The CLI serves both humans (with rich terminal rendering) and AI agents (with structured JSON output).

Hand the [`SKILL.md`](SKILL.md) at the project root to any tool-using agent ([nanobot](https://github.com/HKUDS/nanobot), or any LLM with tool access), and it can configure and operate DeepTutor autonomously.

**One-shot execution** — Run any capability directly from the terminal:

```bash
deeptutor run chat "Explain the Fourier transform" -t rag --kb textbook
deeptutor run deep_solve "Prove that √2 is irrational" -t reason
deeptutor run deep_question "Linear algebra" --config num_questions=5
deeptutor run deep_research "Attention mechanisms in transformers"
deeptutor run visualize "Draw the architecture of a transformer"
```

**Interactive REPL** — A persistent chat session with live mode switching:

```bash
deeptutor chat --capability deep_solve --kb my-kb
# Inside the REPL: /cap, /tool, /kb, /history, /notebook, /config to switch on the fly
```

**Knowledge base lifecycle** — Build, query, and manage RAG-ready collections entirely from the terminal:

```bash
deeptutor kb create my-kb --doc textbook.pdf       # Create from document
deeptutor kb add my-kb --docs-dir ./papers/         # Add a folder of papers
deeptutor kb search my-kb "gradient descent"        # Search directly
deeptutor kb set-default my-kb                      # Set as default for all commands
```

**Dual output mode** — Rich rendering for humans, structured JSON for pipelines:

```bash
deeptutor run chat "Summarize chapter 3" -f rich    # Colored, formatted output
deeptutor run chat "Summarize chapter 3" -f json    # Line-delimited JSON events
```

**Session continuity** — Resume any conversation right where you left off:

```bash
deeptutor session list                              # List all sessions
deeptutor session open <id>                         # Resume in REPL
```

<details>
<summary><b>Full CLI command reference</b></summary>

**Top-level**

| Command | Description |
|:---|:---|
| `deeptutor run <capability> <message>` | Run any capability in a single turn (`chat`, `deep_solve`, `deep_question`, `deep_research`, `math_animator`, `visualize`) |
| `deeptutor chat` | Interactive REPL with optional `--capability`, `--tool`, `--kb`, `--language` |
| `deeptutor serve` | Start the DeepTutor API server |

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

**`deeptutor book`**

| Command | Description |
|:---|:---|
| `deeptutor book list` | List all books in the workspace |
| `deeptutor book health <book_id>` | Check KB drift and book health |
| `deeptutor book refresh-fingerprints <book_id>` | Refresh KB fingerprints and clear stale pages |

**`deeptutor config` / `plugin` / `provider`**

| Command | Description |
|:---|:---|
| `deeptutor config show` | Print current configuration summary |
| `deeptutor plugin list` | List registered tools and capabilities |
| `deeptutor plugin info <name>` | Show tool or capability details |
| `deeptutor provider login <provider>` | Provider auth (`openai-codex` OAuth login; `github-copilot` validates an existing Copilot auth session) |

</details>

---

### 👥 Multi-User — Shared Deployments with Per-User Workspaces

<div align="center">
<img src="assets/figs/dt-multi-user.png" alt="Multi-User" width="800">
</div>

Flip on authentication and DeepTutor turns into a multi-tenant deployment with **per-user isolated workspaces** and **admin-curated resources**. The first person to register becomes the admin and configures models, API keys, and knowledge bases on behalf of everyone else. Subsequent accounts are created by the admin (invite-only), each gets their own scoped chat history / memory / notebooks / knowledge bases, and they only see the LLMs, KBs, and skills the admin assigned to them.

**Quick start (5 steps):**

```bash
# 1. Enable auth in data/user/settings/auth.json:
#    {"enabled": true, "token_expire_hours": 24, "cookie_secure": false}

# 2. Restart the web stack.
deeptutor start

# 3. Open http://localhost:3782/register and create the first account.
#    The first registration is the only public one; that user becomes admin
#    and the /register endpoint is closed automatically afterward.

# 4. As admin, navigate to /admin/users → "Add user" to provision teammates.

# 5. For each user, click the slider icon → assign LLM profiles, knowledge
#    bases, and skills. Save. The user can now sign in and start working.
```

**What the admin sees:**

- **Full Settings page** at `/settings` — manage LLM / embedding / search providers, API keys, model catalogs, and runtime "Apply".
- **User management** at `/admin/users` — create, promote, demote, and delete accounts. The public `/register` endpoint is automatically closed once the first admin exists; further accounts go through `POST /api/v1/auth/users` (admin-only).
- **Grant editor** — for each non-admin user, pick the model profiles, knowledge bases, and skills they may use. Grants carry **logical IDs only**; API keys never cross the grant boundary.
- **Audit trail** — every grant change and assigned-resource access is appended to `multi-user/_system/audit/usage.jsonl`.

**What ordinary users get:**

- **Isolated workspace** under `multi-user/<uid>/` — their own chat history (`chat_history.db`), memory (`SUMMARY.md` / `PROFILE.md`), notebooks, and personal knowledge bases. Nothing is shared by default.
- **Read-only access** to admin-assigned knowledge bases and skills, surfaced inline next to their own resources with an "Assigned by admin" badge.
- **Redacted Settings page** — only theme, language, and a summary of granted models. API keys, base URLs, and provider endpoints are never returned for non-admin requests.
- **Scoped LLM** — chat turns are routed through the admin-assigned model. If no LLM is granted, the turn is rejected up-front (no silent fallback to the admin's keys).

**Workspace layout:**

```
multi-user/
├── _system/
│   ├── auth/users.json          # Hashed credentials, roles
│   ├── auth/auth_secret         # JWT signing secret (auto-generated)
│   ├── grants/<uid>.json        # Per-user resource grants (admin-managed)
│   └── audit/usage.jsonl        # Audit trail
└── <uid>/
    ├── user/
    │   ├── chat_history.db
    │   ├── settings/interface.json
    │   └── workspace/{chat,co-writer,book,...}
    ├── memory/{SUMMARY.md,PROFILE.md}
    └── knowledge_bases/...
```

**Configuration reference:**

| Setting | Required | Description |
|:---|:---|:---|
| `data/user/settings/auth.json: enabled` | Yes | Set to `true` to enable multi-user auth. Default `false` (single-user mode — admin paths everywhere). |
| `multi-user/_system/auth/auth_secret` | Recommended | JWT signing secret. Auto-generated on first authenticated boot if missing. |
| `data/user/settings/auth.json: token_expire_hours` | No | JWT lifetime; defaults to `24`. |
| `data/user/settings/auth.json: username/password_hash` | No | Optional headless single-user bootstrap credential. Leave blank when using browser registration. |
| `data/user/settings/system.json` | No | `deeptutor start` derives frontend auth flags and API base from runtime settings. |

> ⚠️ **PocketBase mode (`integrations.pocketbase_url` set) is single-user only.** The default PocketBase schema has no `role` field on `users` (every login resolves to `role=user`, no admin can be created), and `sessions` / `messages` / `turns` queries are not filtered by `user_id`. Multi-user deployments must keep `integrations.pocketbase_url` blank and use the default JSON/SQLite backend.

> ⚠️ **Single-process recommendation.** The first-user-becomes-admin promotion is protected by an in-process `threading.Lock`. Multi-worker deployments should provision the first admin offline (start with `auth.json.enabled=false`, register the admin via the bootstrap flow, then set `auth.json.enabled=true`) or back the user store with an external system.

## 🗺️ Roadmap

| Status | Milestone |
|:---:|:---|
| 🎯 | **Authentication & Login** — Optional login page for public deployments with multi-user support |
| 🎯 | **Themes & Appearance** — Diverse theme options and customizable UI appearance |
| 🎯 | **Interaction Improvement** — optimize icon design and interaction details |
| 🔜 | **Better Memories** — integrating better memory management |
| 🔜 | **LightRAG Integration** — Integrate [LightRAG](https://github.com/HKUDS/LightRAG) as an advanced knowledge base engine |
| 🔜 | **Documentation Site** — Comprehensive docs page with guides, API reference, and tutorials |

> If you find DeepTutor useful, [give us a star](https://github.com/HKUDS/DeepTutor/stargazers) — it helps us keep going!

---

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

<p align="center">
 <a href="https://www.star-history.com/hkuds/deeptutor">
  <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/badge?repo=HKUDS/DeepTutor&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/badge?repo=HKUDS/DeepTutor" />
   <img alt="Star History Rank" src="https://api.star-history.com/badge?repo=HKUDS/DeepTutor" />
  </picture>
 </a>
</p>

<div align="center">

**[Data Intelligence Lab @ HKU](https://github.com/HKUDS)**

[⭐ Star us](https://github.com/HKUDS/DeepTutor/stargazers) · [🐛 Report a bug](https://github.com/HKUDS/DeepTutor/issues) · [💬 Discussions](https://github.com/HKUDS/DeepTutor/discussions)

---

Licensed under the [Apache License 2.0](LICENSE).

<p>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.DeepTutor&style=for-the-badge&color=00d4ff" alt="Views">
</p>

</div>
