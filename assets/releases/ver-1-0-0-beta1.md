# DeepTutor v1.0.0-beta1 Release Notes

**Release Date:** 2026.03.13

DeepTutor v1.0.0-beta1 is a major architecture release (DeepTutor 2.0), focused on decoupling runtime layers, unifying entry points, and rebuilding the app shell for capability-native workflows.

**Diff Scope:** `main...dev` (733 files changed, 64,336 insertions, 57,258 deletions)

## Highlights

### Agent-Native Runtime (Tools + Capabilities)

- Added new core runtime contracts: `ToolProtocol`, `CapabilityProtocol`, `UnifiedContext`, `StreamEvent`, and `StreamBus`.
- Introduced `ChatOrchestrator` with two runtime registries: `ToolRegistry` (tool discovery, schema export, execution) and `CapabilityRegistry` (capability routing and manifest management).
- Enabled stage-aware streaming and consistent trace events across all entry points.

### Unified Entry Points: CLI / WebSocket / Python Facade

- Added standalone CLI package `deeptutor_cli` with unified commands: `chat`, `run`, `solve`, `quiz`, `research`, `animate`, `kb`, `memory`, `session`, `notebook`, `plugin`, and `serve`.
- Added unified WebSocket endpoint `/api/v1/ws` with turn lifecycle support (`start_turn`, `subscribe_turn`, `subscribe_session`, `resume_from`, `cancel_turn`).
- Added stable app facade (`deeptutor/app/facade.py`) for SDK-style integrations.

### Capability Layer Refactor

- Standardized built-in capabilities: `chat`, `deep_solve` (planning -> reasoning -> writing), `deep_question` (ideation -> generation, plus follow-up mode), `deep_research`, and `math_animator`.
- Unified capability manifests, CLI aliases, request schemas, and stage-level stream events.

### Tooling System Upgrade

- Unified built-in tool wrappers: `brainstorm`, `rag`, `web_search`, `code_execution`, `reason`, `paper_search`, and `geogebra_analysis`.
- Added alias resolution and OpenAI-style schema export in runtime registry.
- Improved observability for tool calls/results through stream events and playground APIs.

### Service Infrastructure Rebuild

- Refactored services into clearer domains: `config`, `llm`, `rag`, `search`, `session`, `memory`, `notebook`, `setup`, and `path_service`.
- Added turn runtime + SQLite-backed session/event persistence with replayable streams.
- Expanded provider routing and multimodal support in LLM services.
- Split dependencies by usage layer: `requirements/core.txt`, `server.txt`, `rag-lite.txt`, `rag-full.txt`, `providers.txt`, `dev.txt`.

### Web Application Restructure

- Reorganized Next.js app shell into workspace/utility route groups: `web/app/(workspace)` and `web/app/(utility)`.
- Added unified chat context and session-aware sidebars.
- Rebuilt core pages/components around capability-driven interaction and trace visualization.

### Security & Stability Improvements

- Hardened code execution with AST-based import/call guards and isolated Python execution mode.
- Added startup validation for capability-to-tool consistency.
- Expanded tests across runtime, tools, CLI, session streaming, and provider layers.

## Breaking Changes

- Package layout migrated from legacy `src/` tree to `deeptutor/` + `deeptutor_cli/`.
- Runtime execution model is now capability-native orchestration (`chat` default, deep modes selected explicitly).
- Web route structure changed significantly; multiple legacy pages/components were removed or relocated.
- Runtime data layout is now centered under `data/user/workspace/...`.
- Optional capabilities/providers require installing matching dependency layers.

## Upgrade Notes

1. Install CLI minimum dependencies: `pip install -r requirements/core.txt`
2. Install API server dependencies (if needed): `pip install -r requirements/server.txt`
3. Install full RAG stack (if needed): `pip install -r requirements/rag-full.txt`
4. Migrate existing runtime data: `python scripts/migrate_user_data.py`
5. Start CLI entry: `deeptutor chat`
6. Start server entry: `deeptutor serve --port 8001`

## What's Changed

- Massive codebase decoupling and runtime unification (DeepTutor 2.0 refactor).
- Introduced capability-first orchestration and standardized tool registry contracts.
- Added standalone CLI operation mode and unified WebSocket turn runtime.
- Rebuilt web app shell and session workflow for capability-native interaction.
- Consolidated service architecture with stronger execution safety and testability.

**Full Changelog**: https://github.com/HKUDS/DeepTutor/compare/main...dev
