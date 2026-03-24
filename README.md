<div align="center">

<img src="assets/logo-ver2.png" alt="DeepTutor Logo" width="150" style="border-radius: 15px;">

# DeepTutor: Towards Agentic Personalized Tutoring

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-3.4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-AGPL--3.0-blue?style=flat-square)](LICENSE)

<p align="center">
  <a href="https://discord.gg/eRsjPgMU4t"><img src="https://img.shields.io/badge/Discord-Join_Community-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
  &nbsp;&nbsp;
  <a href="./Communication.md"><img src="https://img.shields.io/badge/Feishu-Join_Group-00D4AA?style=for-the-badge&logo=feishu&logoColor=white" alt="Feishu"></a>
  &nbsp;&nbsp;
  <a href="https://github.com/HKUDS/DeepTutor/issues/78"><img src="https://img.shields.io/badge/WeChat-Join_Group-07C160?style=for-the-badge&logo=wechat&logoColor=white" alt="WeChat"></a>
</p>

[**Quick Start**](#-quick-start) · [**Architecture**](#-agent-native-architecture) · [**Capabilities**](#-capabilities) · [**Develop**](#-extending-deeptutor) · [**FAQ**](#-faq)

[🇨🇳 中文](assets/README/README_CN.md) · [🇯🇵 日本語](assets/README/README_JA.md) · [🇪🇸 Español](assets/README/README_ES.md) · [🇫🇷 Français](assets/README/README_FR.md) · [🇸🇦 العربية](assets/README/README_AR.md) · [🇷🇺 Русский](assets/README/README_RU.md) · [🇮🇳 हिन्दी](assets/README/README_HI.md) · [🇵🇹 Português](assets/README/README_PT.md)

</div>

> **DeepTutor** is an open-source, **agent-native** intelligent tutoring system that treats every learning interaction as an agentic workflow. Instead of wrapping a single LLM behind a chat interface, DeepTutor orchestrates **specialized agents** — each with its own tools, memory, and reasoning loop — to deliver personalized, multi-step tutoring across problem solving, assessment generation, deep research, and interactive learning.

---
### 📰 News

> **[2026.1.1]** Happy New Year! Join our [Discord Community](https://discord.gg/eRsjPgMU4t), [Wechat Community](https://github.com/HKUDS/DeepTutor/issues/78), or [Discussions](https://github.com/HKUDS/DeepTutor/discussions) - shape the future of DeepTutor! 💬

> **[2025.12.30]** Visit our [Official Website](https://hkuds.github.io/DeepTutor/) for more details!

> **[2025.12.29]** DeepTutor is now live! ✨

### 📦 Releases

> **[2026.1.23]** Release [v0.6.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.6.0) - Frontend session persistence, full Chinese support, Docker deployment updates, and minor bug fixes -- Thanks for all the feedback!

<details>
<summary>History releases</summary>

> **[2026.1.18]** Release [v0.5.2](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.1) - Enhance RAG pipeline with Docling support and improve CI/CD workflows with several minor bugs fixed -- Thanks to all the feedbacks!


> **[2026.1.15]** Release [v0.5.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.5.0) - Unified LLM & Embedding services, RAG pipeline selection, and major enhancements to Home, History, QuestionGen & Settings modules -- Thanks to all the contributors!

> **[2026.1.9]** Release [v0.4.1](https://github.com/HKUDS/DeepTutor/releases/tag/v0.4.1) with LLM Provider system overhaul, Question Generation robustness improvements, and codebase cleanup - Thanks to all the contributors!

> **[2026.1.9]** Release [v0.4.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.4.0) with new code structure, multiple llm & embeddings support - Thanks to all the contributors!

> **[2026.1.5]** [v0.3.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.3.0) - Unified PromptManager architecture, CI/CD automation & pre-built Docker images on GHCR

> **[2026.1.2]** [v0.2.0](https://github.com/HKUDS/DeepTutor/releases/tag/v0.2.0) - Docker deployment, Next.js 16 & React 19 upgrade, WebSocket security & critical vulnerability fixes

</details>

---

## Why Agentic Tutoring?

Traditional AI tutoring is **single-turn Q&A** — you ask, the model answers, context is lost. DeepTutor takes a fundamentally different approach: every interaction is an **agentic workflow** where specialized agents plan, reason, act, and verify.

| Dimension | Traditional AI Tutor | DeepTutor |
|:---|:---|:---|
| **Reasoning** | Single LLM call | Multi-agent pipelines with planning, execution, and verification stages |
| **Memory** | Stateless or shallow context | Persistent memory with knowledge graphs, vector stores, and session tracking |
| **Output** | Plain text | Rich artifacts: interactive visualizations, code execution, citations, audio |
| **Adaptation** | One-size-fits-all | Grounded in your documents, learning history, and goals |
| **Extensibility** | Monolithic | Two-layer plugin architecture — add tools or capabilities without touching the core |

---

## 🏗 Agent-Native Architecture

DeepTutor is built on a **two-layer plugin model** with a unified orchestrator that routes every request — whether from CLI, WebSocket, or Python SDK — to the right agents and tools.

```
Entry Points:    CLI (Typer)  ·  WebSocket API  ·  Python SDK
                         ↓              ↓             ↓
              ┌──────────────────────────────────────────────┐
              │             ChatOrchestrator                  │
              │   routes to default ChatCapability            │
              │   or a selected deep Capability               │
              └──────────┬─────────────────┬─────────────────┘
                         │                 │
              ┌──────────▼──────┐  ┌───────▼────────────┐
              │  Tool Registry  │  │ Capability Registry │
              │   (Level 1)     │  │    (Level 2)        │
              └─────────────────┘  └────────────────────┘
```

### Level 1 — Tools

Lightweight, single-function utilities the LLM calls on demand:

| Tool | Description |
|:---|:---|
| `rag` | Hybrid knowledge-base retrieval (naive + graph-enhanced) |
| `web_search` | Real-time web search with structured citations |
| `code_execution` | Sandboxed Python execution with artifact capture |
| `reason` | Dedicated deep-reasoning LLM call |
| `brainstorm` | Breadth-first idea exploration with rationale |
| `paper_search` | arXiv academic paper search |
| `geogebra_analysis` | Image → GeoGebra commands (4-stage vision pipeline) |

### Level 2 — Capabilities

Multi-step agent pipelines that take full control of the conversation:

| Capability | Stages | Description |
|:---|:---|:---|
| `chat` | responding | Default tool-augmented conversational tutoring |
| `deep_solve` | planning → reasoning → writing | Dual-loop multi-agent problem solving |
| `deep_question` | ideation → evaluation → generation → validation | Assessment generation with auto-validation |

### Plugins

Community-extensible capabilities loaded from `deeptutor/plugins/`:

| Plugin | Type | Description |
|:---|:---|:---|
| `deep_research` | playground | Multi-agent research with dynamic topic queues and cited reports |

<div align="center">
<img src="assets/figs/full-pipe.png" alt="DeepTutor Full-Stack Architecture" width="100%">
</div>

---

## ✨ Capabilities

<div align="center">
  <img src="assets/figs/title_gradient.svg" alt="All-in-One Agentic Tutoring" width="70%">
</div>

### 📚 Agentic Problem Solving

Upload textbooks, papers, or technical documents to build your knowledge base. When you ask a question, DeepTutor doesn't just retrieve — it **plans, investigates, solves, and verifies** through a dual-loop multi-agent pipeline with precise source citations.

<table>
<tr>
<td width="50%" align="center" valign="top">

<h4>Multi-Agent Solver</h4>
<a href="#-smart-solver">
<img src="assets/gifs/solve.gif" width="100%">
</a>
<br>
<sub>Analysis Loop → Solve Loop with RAG, web search, and code execution</sub>

</td>
<td width="50%" align="center" valign="top">

<h4>Interactive Guided Learning</h4>
<a href="#-guided-learning">
<img src="assets/gifs/guided-learning.gif" width="100%">
</a>
<br>
<sub>Personalized visual explanations with progressive knowledge paths</sub>

</td>
</tr>
</table>

### 🎯 Adaptive Knowledge Reinforcement

The question generation agent autonomously designs assessments tailored to your knowledge level. **Custom mode** generates questions grounded in your knowledge base; **Mimic mode** clones the style and difficulty of uploaded reference exams.

<table>
<tr>
<td width="50%" valign="top" align="center">

<a href="#-question-generator">
<img src="assets/gifs/question-1.gif" width="100%">
</a>

**Custom Questions**
<sub>Auto-validated practice from your knowledge base</sub>

</td>
<td width="50%" valign="top" align="center">

<a href="#-question-generator">
<img src="assets/gifs/question-2.gif" width="100%">
</a>

**Mimic Questions**
<sub>Clone exam style for authentic practice</sub>

</td>
</tr>
</table>

### 🔍 Deep Research & Co-Writer

The deep research plugin decomposes topics into a dynamic queue of subtopics, dispatches parallel research agents equipped with RAG, web search, and paper search, then synthesizes a fully cited academic-style report.

<table>
<tr>
<td width="50%" align="center">

<a href="#-deep-research">
<img src="assets/gifs/deepresearch.gif" width="100%">
</a>

**Deep Research**
<sub>Planning → Parallel Research → Cited Report Generation</sub>

</td>
<td width="50%" align="center">

<a href="#-interactive-ideagen-co-writer">
<img src="assets/gifs/co-writer.gif" width="100%">
</a>

**Co-Writer**
<sub>AI-assisted writing with RAG context, annotation, and TTS narration</sub>

</td>
</tr>
</table>

### 🏗️ Personal Knowledge Infrastructure

<table>
<tr>
<td width="50%" align="center">

<a href="#-dashboard--knowledge-base-management">
<img src="assets/gifs/knowledge_bases.png" width="100%">
</a>

**Knowledge Base**
<sub>Upload, organize, and incrementally update your document collections</sub>

</td>
<td width="50%" align="center">

<a href="#-notebook">
<img src="assets/gifs/notebooks.png" width="100%">
</a>

**Notebook**
<sub>Persistent learning memory across all sessions and modules</sub>

</td>
</tr>
</table>

<p align="center">
  <sub>🌙 Dark mode supported</sub>
</p>

---

## 🚀 Quick Start

### Step 1: Clone & Configure

```bash
git clone https://github.com/HKUDS/DeepTutor.git
cd DeepTutor
cp .env.example .env
# Edit .env with your API keys
```

<details>
<summary>📋 <b>Environment Variables Reference</b></summary>

| Variable | Required | Description |
|:---|:---:|:---|
| `BACKEND_PORT` | No | Backend API port (default: `8001`) |
| `FRONTEND_PORT` | No | Frontend port (default: `3782`) |
| `LLM_BINDING` | **Yes** | LLM provider binding (e.g., `openai`, `anthropic`) |
| `LLM_MODEL` | **Yes** | Model name (e.g., `gpt-4o`) |
| `LLM_API_KEY` | **Yes** | Your LLM API key |
| `LLM_HOST` | **Yes** | API endpoint URL |
| `LLM_API_VERSION` | No | API version for Azure/OpenAI-compatible providers |
| `EMBEDDING_BINDING` | **Yes** | Embedding provider binding (e.g., `openai`, `jina`) |
| `EMBEDDING_MODEL` | **Yes** | Embedding model name |
| `EMBEDDING_API_KEY` | **Yes** | Embedding API key |
| `EMBEDDING_HOST` | **Yes** | Embedding API endpoint |
| `EMBEDDING_DIMENSION` | **Yes** | Embedding vector dimension |
| `EMBEDDING_API_VERSION` | No | API version for Azure/OpenAI-compatible embeddings |
| `SEARCH_PROVIDER` | No | Search provider (`perplexity`, `openrouter`, `tavily`, `serper`, `jina`, `exa`, `baidu`) |
| `SEARCH_API_KEY` | No | Unified API key for all search providers |
| `SEARCH_BASE_URL` | No | Custom search endpoint URL |
| `NEXT_PUBLIC_API_BASE_EXTERNAL` | No | Public backend URL for cloud deployment |
| `NEXT_PUBLIC_API_BASE` | No | Alternative direct API base URL |
| `DISABLE_SSL_VERIFY` | No | Disable SSL verification (keep `false` in production) |

</details>

### Step 2: Launch

#### 🐳 Option A: Docker (Recommended)

> No Python/Node.js setup required — just Docker.

```bash
# Build from source
docker compose up                  # ~11 min first run on Mac Mini M4

# Or use pre-built image (faster, auto-detects architecture)
docker run -d --name deeptutor \
  -p 8001:8001 -p 3782:3782 \
  --env-file .env \
  -v $(pwd)/data/user:/app/data/user \
  -v $(pwd)/data/knowledge_bases:/app/data/knowledge_bases \
  ghcr.io/hkuds/deeptutor:latest
# Windows PowerShell: use ${PWD} instead of $(pwd)
```

<details>
<summary>📋 <b>Docker Commands & Image Tags</b></summary>

```bash
docker compose up -d              # Start in background
docker compose down               # Stop
docker compose logs -f            # View logs
docker compose up --build         # Rebuild after changes
docker compose build --no-cache   # Full rebuild
```

| Tag | Architectures | Description |
|:----|:--------------|:------------|
| `:latest` | AMD64 + ARM64 | Latest stable (auto-detects) |
| `:X.Y.Z` | AMD64 + ARM64 | Specific version |
| `:X.Y.Z-amd64` | AMD64 only | Explicit AMD64 |
| `:X.Y.Z-arm64` | ARM64 only | Explicit ARM64 |

For cloud deployment, see `docs/guide/docker-start.md`.

</details>

#### 💻 Option B: Manual Installation

> For development or non-Docker environments. Requires Python 3.10+, Node.js 18+.

```bash
# Create environment
conda create -n deeptutor python=3.10 && conda activate deeptutor
# Or: python -m venv venv && source venv/bin/activate

# Install
pip install -e .
pip install ".[server]"            # Web/API support
pip install ".[math-animator]"     # Optional math animator

# Interactive setup (ports, providers, .env)
python scripts/start_tour.py

# Launch
python scripts/start_web.py        # Web UI + Backend
# Or: deeptutor chat               # CLI-only mode
```

<details>
<summary>🔧 <b>Start Frontend & Backend Separately</b></summary>

**Backend** (FastAPI):
```bash
python -m deeptutor.api.run_server
# Or: uvicorn deeptutor.api.main:app --host 0.0.0.0 --port 8001 --reload
```

**Frontend** (Next.js):
```bash
cd web && npm install && npm run dev -- -p 3782
```

| Service | Default Port |
|:---:|:---:|
| Backend | `8001` |
| Frontend | `3782` |

</details>

### Access

| Service | URL | Description |
|:---:|:---|:---|
| **Web UI** | http://localhost:3782 | Main web interface |
| **API Docs** | http://localhost:8001/docs | Interactive API documentation |

### Demo Knowledge Bases (Optional)

1. Download from [Google Drive](https://drive.google.com/drive/folders/1iWwfZXiTuQKQqUYb5fGDZjLCeTUP6DA6?usp=sharing)
2. Extract into `data/` directory

> Demo KBs use `text-embedding-3-large` with `dimensions = 3072`

Available demos: **Research Papers** (5 papers from [AI-Researcher](https://github.com/HKUDS/AI-Researcher), [LightRAG](https://github.com/HKUDS/LightRAG), etc.) and **Data Science Textbook** (8 chapters, 296 pages from [this book](https://ma-lab-berkeley.github.io/deep-representation-learning-book/)).

---

## 🧩 Extending DeepTutor

DeepTutor's two-layer architecture is designed for extensibility. Add new tools or capabilities without modifying the core.

### Plugin Development

Create a directory under `deeptutor/plugins/<name>/`:

```
manifest.yaml     # Plugin metadata and stage definitions
capability.py     # Class extending BaseCapability
```

**manifest.yaml**:
```yaml
name: my_plugin
version: 0.1.0
type: playground
description: "My custom plugin"
stages: [step1, step2]
```

**capability.py**:
```python
from deeptutor.core.capability_protocol import BaseCapability, CapabilityManifest
from deeptutor.core.context import UnifiedContext
from deeptutor.core.stream_bus import StreamBus

class MyPlugin(BaseCapability):
    manifest = CapabilityManifest(
        name="my_plugin",
        description="My custom plugin",
        stages=["step1", "step2"],
    )

    async def run(self, context: UnifiedContext, stream: StreamBus) -> None:
        async with stream.stage("step1", source=self.name):
            await stream.content("Working on step 1...", source=self.name)
        await stream.result({"response": "Done!"}, source=self.name)
```

### CLI

```bash
deeptutor run chat "Explain Fourier transform"
deeptutor run deep_solve "Solve x^2=4" -t rag --kb my-kb
deeptutor run deep_question "Linear algebra" --config num_questions=5
deeptutor chat                        # Interactive REPL
deeptutor kb list | create | add      # Knowledge base management
deeptutor plugin list                 # Available plugins
deeptutor serve --port 8001           # Start API server
```

### Key Source Files

| Path | Purpose |
|:---|:---|
| `deeptutor/runtime/orchestrator.py` | ChatOrchestrator — unified entry point |
| `deeptutor/core/tool_protocol.py` | `BaseTool` abstract class |
| `deeptutor/core/capability_protocol.py` | `BaseCapability` abstract class |
| `deeptutor/core/context.py` | `UnifiedContext` dataclass |
| `deeptutor/core/stream.py` / `stream_bus.py` | StreamEvent protocol & async fan-out |
| `deeptutor/runtime/registry/` | Tool & Capability discovery and registration |
| `deeptutor/capabilities/` | Built-in capability implementations |
| `deeptutor/tools/builtin/` | Built-in tool implementations |
| `deeptutor/plugins/` | Community plugins |
| `deeptutor_cli/main.py` | Typer CLI entry point |
| `deeptutor/api/routers/unified_ws.py` | Unified WebSocket endpoint |

### Dependency Layers

```
requirements/cli.txt            — CLI (LLM + RAG + providers + tools)
requirements/server.txt         — CLI + FastAPI/uvicorn (Web/API)
requirements/math-animator.txt  — Manim addon (deeptutor animate)
requirements/dev.txt            — Server + test/lint tools
```

---

## 📂 Data Layout

All user content lives under `data/`:

```
data/
├── knowledge_bases/                    # Document collections with vector indices
└── user/
    ├── chat_history.db                 # Unified conversation database
    ├── logs/                           # Runtime logs
    ├── settings/                       # Runtime config (auto-bootstrapped)
    │   ├── interface.json
    │   ├── main.yaml
    │   └── agents.yaml
    └── workspace/
        ├── memory/                     # Agent memory persistence
        ├── notebook/                   # Learning record notebooks
        ├── co-writer/                  # Co-writer drafts, audio, tool calls
        ├── guide/                      # Guided learning sessions
        └── chat/
            ├── chat/                   # Standard chat logs
            ├── deep_solve/             # Problem solving artifacts
            ├── deep_question/          # Generated assessments
            ├── deep_research/          # Research reports & caches
            └── _detached_code_execution/
```

---

## 📋 Roadmap

> 🌟 Star to follow our progress!

- [x] Multi-language support
- [x] Community channels (Discord, WeChat, Feishu)
- [x] Video & audio file support
- [x] Atomic RAG pipeline customization
- [ ] Incremental knowledge-base editing
- [ ] Personalized learner workspace
- [ ] Knowledge graph visualization
- [ ] Online demo

---

## 📦 Module Deep Dives

<details>
<summary><b>🧠 Smart Solver</b> — Dual-loop multi-agent problem solving</summary>

<details>
<summary><b>Architecture Diagram</b></summary>

![Smart Solver Architecture](assets/figs/solve.png)

</details>

**Analysis Loop + Solve Loop** dual-loop architecture with multi-mode reasoning and dynamic knowledge retrieval.

| Feature | Description |
|:---|:---|
| Dual-Loop Architecture | **Analysis Loop**: InvestigateAgent → NoteAgent &nbsp;&nbsp; **Solve Loop**: PlanAgent → ManagerAgent → SolveAgent → CheckAgent → Format |
| Multi-Agent Collaboration | Specialized agents for investigation, note-taking, planning, management, solving, and checking |
| Tool Integration | RAG (naive/hybrid), Web Search, Query Item, Code Execution |
| Real-time Streaming | WebSocket transmission with live reasoning process display |
| Citation Management | Structured citations with reference tracking |

<details>
<summary><b>Python API</b></summary>

```python
import asyncio
from deeptutor.agents.solve import MainSolver

async def main():
    solver = MainSolver(kb_name="ai_textbook")
    result = await solver.solve(
        question="Calculate the linear convolution of x=[1,2,3] and h=[4,5]",
        mode="auto"
    )
    print(result['formatted_solution'])

asyncio.run(main())
```

</details>

<details>
<summary><b>Output Structure</b></summary>

```
data/user/workspace/chat/deep_solve/solve_YYYYMMDD_HHMMSS/
├── investigate_memory.json    # Analysis Loop memory
├── solve_chain.json           # Solve Loop steps & tool records
├── citation_memory.json       # Citation management
├── final_answer.md            # Final solution (Markdown)
├── performance_report.json    # Performance monitoring
└── artifacts/                 # Code execution outputs
```

</details>

</details>

---

<details>
<summary><b>📝 Question Generator</b> — Dual-mode assessment creation with auto-validation</summary>

<details>
<summary><b>Architecture Diagram</b></summary>

![Question Generator Architecture](assets/figs/question-gen.png)

</details>

Two generation modes: **Custom** (knowledge-base-grounded questions) and **Mimic** (clone reference exam style).

| Feature | Description |
|:---|:---|
| Custom Mode | Background Knowledge → Question Planning → Generation → Single-Pass Validation |
| Mimic Mode | PDF Upload → MinerU Parsing → Question Extraction → Style Mimicking |
| ReAct Engine | QuestionGenerationAgent with autonomous think → act → observe loop |
| Question Types | Multiple choice, fill-in-the-blank, calculation, written response, etc. |
| Batch Processing | Parallel generation with progress tracking |

<details>
<summary><b>Python API</b></summary>

**Custom Mode:**
```python
import asyncio
from deeptutor.agents.question import AgentCoordinator

async def main():
    coordinator = AgentCoordinator(
        kb_name="ai_textbook",
        output_dir="data/user/workspace/chat/deep_question"
    )
    result = await coordinator.generate_questions_custom(
        requirement_text="Generate 3 medium-difficulty questions about deep learning basics",
        difficulty="medium",
        question_type="choice",
        count=3
    )
    print(f"Generated {result['completed']}/{result['requested']} questions")

asyncio.run(main())
```

**Mimic Mode:**
```python
from deeptutor.agents.question.tools.exam_mimic import mimic_exam_questions

result = await mimic_exam_questions(
    pdf_path="exams/midterm.pdf",
    kb_name="calculus",
    output_dir="data/user/workspace/chat/deep_question/mimic_papers",
    max_questions=5
)
print(f"Generated {result['successful_generations']} questions")
```

</details>

<details>
<summary><b>Output Structure</b></summary>

**Custom Mode:**
```
data/user/workspace/chat/deep_question/custom_YYYYMMDD_HHMMSS/
├── background_knowledge.json
├── question_plan.json
├── question_1_result.json
└── ...
```

**Mimic Mode:**
```
data/user/workspace/chat/deep_question/mimic_papers/
└── mimic_YYYYMMDD_HHMMSS_{pdf_name}/
    ├── {pdf_name}.pdf
    ├── auto/{pdf_name}.md
    ├── {pdf_name}_YYYYMMDD_HHMMSS_questions.json
    └── {pdf_name}_YYYYMMDD_HHMMSS_generated_questions.json
```

</details>

</details>

---

<details>
<summary><b>🎓 Guided Learning</b> — Progressive learning paths with interactive visualization</summary>

<details>
<summary><b>Architecture Diagram</b></summary>

![Guided Learning Architecture](assets/figs/guide.png)

</details>

Multi-agent pipeline that converts notebook content into progressive, interactive learning experiences.

| Agent | Responsibility |
|:---|:---|
| **LocateAgent** | Identifies 3–5 progressive knowledge points from notebook content |
| **InteractiveAgent** | Converts knowledge points into visual HTML pages |
| **ChatAgent** | Provides context-aware Q&A during learning |
| **SummaryAgent** | Generates learning summaries on completion |

**Flow**: Select Notebooks → Generate Plan → Interactive Visual Learning → Q&A → Summary

</details>

---

<details>
<summary><b>✏️ Co-Writer</b> — AI-assisted writing with context and narration</summary>

<details>
<summary><b>Architecture Diagram</b></summary>

![Co-Writer Architecture](assets/figs/co-writer.png)

</details>

Intelligent Markdown editor supporting AI rewriting, auto-annotation, and TTS narration.

| Feature | Description |
|:---|:---|
| EditAgent | Rewrite (custom instructions + optional RAG/web), Shorten, Expand |
| Auto-Annotation | Key content identification and marking |
| NarratorAgent | Script generation + TTS with multiple voice options |
| Context Enhancement | Optional RAG or web search for richer content |

</details>

---

<details>
<summary><b>🔬 Deep Research</b> — Multi-agent research with dynamic topic queues</summary>

<details>
<summary><b>Architecture Diagram</b></summary>

![Deep Research Architecture](assets/figs/deepresearch.png)

</details>

**DR-in-KG** (Deep Research in Knowledge Graph) — three-phase research pipeline: **Planning → Researching → Reporting** with dynamic topic discovery and centralized citation management.

| Phase | Agents | Description |
|:---|:---|:---|
| **Planning** | RephraseAgent, DecomposeAgent | Topic optimization and subtopic decomposition |
| **Researching** | ManagerAgent, ResearchAgent, NoteAgent | Queue-based research with RAG, web, paper search, code execution |
| **Reporting** | ReportingAgent | Outline generation, section writing with citation tables, post-processing |

**Execution Modes**: Series (sequential) or Parallel (concurrent with `AsyncCitationManagerWrapper`).

**Presets**: `quick` (1–2 subtopics) · `medium` (5 subtopics) · `deep` (8 subtopics) · `auto` (agent decides).

<details>
<summary><b>Citation System</b></summary>

```
┌─────────────────────────────────────────────────────────┐
│                    CitationManager                       │
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐  │
│  │ ID Generation │  │ ref_number    │  │Deduplication│  │
│  │ PLAN-XX       │  │ Mapping       │  │(papers)     │  │
│  │ CIT-X-XX      │  │               │  │             │  │
│  └───────┬───────┘  └───────┬───────┘  └──────┬──────┘  │
└──────────┼──────────────────┼─────────────────┼─────────┘
           │                  │                 │
    ┌──────▼──────┐    ┌──────▼──────┐   ┌──────▼──────┐
    │Research     │    │Reporting    │   │ References  │
    │Agents       │    │Agent [N]    │   │  Section    │
    └─────────────┘    └─────────────┘   └─────────────┘
```

Centralized citation management with thread-safe async operations, sequential ref_number mapping, and automatic `[N]` → `[[N]](#ref-N)` post-processing.

</details>

<details>
<summary><b>Python API</b></summary>

```python
import asyncio
from deeptutor.agents.research import ResearchPipeline
from deeptutor.services.config import load_config_with_main
from deeptutor.services.llm import get_llm_config

async def main():
    config = load_config_with_main("main.yaml")
    llm_config = get_llm_config()
    pipeline = ResearchPipeline(
        config=config,
        api_key=llm_config["api_key"],
        base_url=llm_config["base_url"],
        kb_name="ai_textbook"
    )
    result = await pipeline.run(topic="Attention Mechanisms in Deep Learning")
    print(f"Report saved to: {result['final_report_path']}")

asyncio.run(main())
```

</details>

<details>
<summary><b>Output Structure</b></summary>

```
data/user/workspace/chat/deep_research/
├── reports/
│   ├── research_YYYYMMDD_HHMMSS.md        # Report with [[N]](#ref-N) citations
│   └── research_*_metadata.json            # Research metadata
└── cache/
    └── research_YYYYMMDD_HHMMSS/
        ├── queue.json                       # Topic queue state
        ├── citations.json                   # Citation registry
        ├── step1_planning.json              # Planning results
        ├── outline.json                     # Report outline
        └── token_cost_summary.json          # Usage statistics
```

</details>

<details>
<summary><b>Configuration</b></summary>

```yaml
# data/user/settings/agents.yaml
research:
  temperature: 0.5
  max_tokens: 12000

# data/user/settings/main.yaml
research:
  researching:
    note_agent_mode: auto
    tool_timeout: 60
    tool_max_retries: 2
    paper_search_years_limit: 3
tools:
  web_search:
    enabled: true
```

</details>

</details>

---

<details>
<summary><b>📊 Dashboard & Knowledge Base</b></summary>

Unified system entry with activity tracking, knowledge base management, and system status monitoring.

| Feature | Description |
|:---|:---|
| Activity Statistics | Recent solving, generation, and research records |
| Knowledge Base Management | Create, upload, update, delete knowledge bases |
| Notebook Statistics | Record counts and distribution |
| Quick Actions | One-click access to all modules |

**Create a Knowledge Base**: Web UI at `/knowledge` → "New Knowledge Base" → Upload PDF/TXT/MD files.

**CLI**: `deeptutor kb create <name> --doc <path>` / `deeptutor kb add <name> --doc <path>` (incremental).

</details>

---

<details>
<summary><b>📓 Notebook</b></summary>

Unified learning record management connecting outputs from all modules.

- Create, edit, and organize multiple notebooks
- Auto-categorized records from solving, generation, research, and co-writing
- Custom colors and icons
- Cross-module integration via "Add to Notebook" action

</details>

---

## 🧪 CI

| Workflow | Description |
|:---|:---|
| [`tests.yml`](.github/workflows/tests.yml) | Import checks (Python 3.10/3.11/3.12) + smoke tests (3.11) |
| [`linting.yaml`](.github/workflows/linting.yaml) | Python pre-commit + frontend lint/type-check |
| [`docker-publish.yml`](.github/workflows/docker-publish.yml) | Manual multi-arch image publish |

```bash
# Local smoke test (aligned with CI)
pytest -q --import-mode=importlib tests/api tests/cli tests/services/test_app_facade.py tests/services/test_model_catalog.py tests/services/test_path_service.py tests/services/memory tests/services/session tests/tools
```

---

## ❓ FAQ

<details>
<summary><b>Backend fails to start?</b></summary>

- Confirm Python >= 3.10 and dependencies installed (`pip install -e ".[server]"`)
- Check if port 8001 is in use — change with `BACKEND_PORT=9001` in `.env`
- Review terminal error messages

</details>

<details>
<summary><b>Port occupied after Ctrl+C?</b></summary>

Ctrl+C sometimes only terminates the frontend. Kill the backend manually:

```bash
# macOS/Linux
lsof -i :8001 && kill -9 <PID>

# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

</details>

<details>
<summary><b>npm: command not found?</b></summary>

```bash
# Option A: Conda (recommended)
conda install -c conda-forge nodejs

# Option B: nvm
nvm install 18 && nvm use 18

# Option C: Official installer from https://nodejs.org/
```

Verify: `node --version` (should be v18+), `npm --version`.

</details>

<details>
<summary><b>Long path names on Windows?</b></summary>

Enable long path support:

```cmd
reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f
```

Restart your terminal after running this command.

</details>

<details>
<summary><b>Frontend cannot connect to backend?</b></summary>

- Confirm backend is running: visit http://localhost:8001/docs
- Re-run `python scripts/start_tour.py` then `python scripts/start_web.py`

</details>

<details>
<summary><b>HTTPS reverse proxy issues (Settings page error)?</b></summary>

Fixed in v0.5.0+. For older versions, the issue was FastAPI generating HTTP redirects behind HTTPS proxy.

**Solution**: Update to latest version. Set `NEXT_PUBLIC_API_BASE=https://your-domain.com:port` in `.env`.

See [nginx configuration example](https://github.com/HKUDS/DeepTutor/issues/112) and `docs/guide/docker-start.md`.

</details>

<details>
<summary><b>WebSocket connection fails?</b></summary>

- Confirm backend is running and firewall allows the port
- Verify URL format: `ws://localhost:8001/api/v1/...`
- Check backend logs for errors

</details>

<details>
<summary><b>Where are module outputs stored?</b></summary>

| Module | Path |
|:---|:---|
| Solve | `data/user/workspace/chat/deep_solve/solve_YYYYMMDD_HHMMSS/` |
| Question | `data/user/workspace/chat/deep_question/{custom\|mimic}_YYYYMMDD_HHMMSS/` |
| Research | `data/user/workspace/chat/deep_research/reports/` |
| Co-Writer | `data/user/workspace/co-writer/` |
| Notebook | `data/user/workspace/notebook/` |
| Guide | `data/user/workspace/guide/session_{session_id}.json` |
| Logs | `data/user/logs/` |

</details>

---

## ⭐ Star History

<div align="center">

<p>
  <a href="https://github.com/HKUDS/DeepTutor/stargazers"><img src="assets/roster/stargazers.svg" alt="Stargazers"/></a>
  &nbsp;&nbsp;
  <a href="https://github.com/HKUDS/DeepTutor/network/members"><img src="assets/roster/forkers.svg" alt="Forkers"/></a>
</p>

<a href="https://www.star-history.com/#HKUDS/DeepTutor&type=timeline&legend=top-left">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&legend=top-left" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=HKUDS/DeepTutor&type=timeline&legend=top-left" />
  </picture>
</a>

</div>

## 🤝 Contribution

<div align="center">

We hope DeepTutor could become a gift for the community. 🎁

<a href="https://github.com/HKUDS/DeepTutor/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HKUDS/DeepTutor&max=999" alt="Contributors to HKUDS/DeepTutor" />
</a>

</div>

## 🔗 Related Projects

<div align="center">

| [⚡ LightRAG](https://github.com/HKUDS/LightRAG) | [🎨 RAG-Anything](https://github.com/HKUDS/RAG-Anything) | [💻 DeepCode](https://github.com/HKUDS/DeepCode) | [🔬 AI-Researcher](https://github.com/HKUDS/AI-Researcher) |
|:---:|:---:|:---:|:---:|
| Simple and Fast RAG | Multimodal RAG | AI Code Assistant | Research Automation |

**[Data Intelligence Lab @ HKU](https://github.com/HKUDS)**

[⭐ Star us](https://github.com/HKUDS/DeepTutor/stargazers) · [🐛 Report a bug](https://github.com/HKUDS/DeepTutor/issues) · [💬 Discussions](https://github.com/HKUDS/DeepTutor/discussions)

---

This project is licensed under the ***[AGPL-3.0 License](LICENSE)***.

<p align="center">
  <em> Thanks for visiting ✨ DeepTutor!</em><br><br>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.DeepTutor&style=for-the-badge&color=00d4ff" alt="Views">
</p>

</div>
