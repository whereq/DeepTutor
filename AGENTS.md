# DeepTutor — Agent-Native Architecture

## Overview

DeepTutor is an **agent-native** intelligent learning companion built around
a two-layer plugin model (Tools + Capabilities) with three entry points:
CLI, WebSocket API, and Python SDK.

## Architecture

```
Entry Points:  CLI (Typer)  |  WebSocket /api/v1/ws  |  Python SDK
                    ↓                   ↓                   ↓
              ┌─────────────────────────────────────────────────┐
              │              ChatOrchestrator                    │
              │   routes to ChatCapability (default)             │
              │   or a selected deep Capability                  │
              └──────────┬──────────────┬───────────────────────┘
                         │              │
              ┌──────────▼──┐  ┌────────▼──────────┐
              │ ToolRegistry │  │ CapabilityRegistry │
              │  (Level 1)   │  │   (Level 2)        │
              └──────────────┘  └────────────────────┘
```

### Level 1 — Tools

Lightweight single-function tools the LLM calls on demand:

| Tool                | Description                                    |
| ------------------- | ---------------------------------------------- |
| `rag`               | Knowledge base retrieval (RAG)                 |
| `web_search`        | Web search with citations                      |
| `code_execution`    | Sandboxed Python execution                     |
| `reason`            | Dedicated deep-reasoning LLM call              |
| `brainstorm`        | Breadth-first idea exploration with rationale  |
| `paper_search`      | arXiv academic paper search                    |
| `geogebra_analysis` | Image → GeoGebra commands (4-stage vision pipeline) |

### Level 2 — Capabilities

Multi-step agent pipelines that take over the conversation:

| Capability       | Stages                                         |
| ---------------- | ---------------------------------------------- |
| `chat`           | responding (default, tool-augmented)           |
| `deep_solve`     | planning → reasoning → writing                 |
| `deep_question`  | ideation → evaluation → generation → validation |

### Playground Plugins

Extended features in `src/plugins/`:

| Plugin            | Type       | Description                          |
| ----------------- | ---------- | ------------------------------------ |
| `deep_research`   | playground | Multi-agent research + reporting     |

## CLI Usage

```bash
# Install (CLI only, ~80MB)
pip install -r requirements/core.txt

# Chat
deeptutor chat
deeptutor chat --once "Solve x^2=4" --capability deep-solve --tool rag

# Knowledge bases
deeptutor kb list
deeptutor kb create my-kb --doc textbook.pdf

# Memory
deeptutor memory show

# Plugins
deeptutor plugin list

# API server (requires requirements/server.txt)
deeptutor serve --port 8001
```

## Key Files

| Path                          | Purpose                              |
| ----------------------------- | ------------------------------------ |
| `src/runtime/orchestrator.py` | ChatOrchestrator — unified entry     |
| `src/core/stream.py`          | StreamEvent protocol                 |
| `src/core/stream_bus.py`      | Async event fan-out                  |
| `src/core/tool_protocol.py`   | BaseTool abstract class              |
| `src/core/capability_protocol.py` | BaseCapability abstract class    |
| `src/core/context.py`         | UnifiedContext dataclass             |
| `src/runtime/registry/tool_registry.py` | Tool discovery & registration |
| `src/runtime/registry/capability_registry.py` | Capability discovery & registration |
| `src/runtime/mode.py`         | RunMode (CLI vs SERVER)              |
| `src/capabilities/`           | Built-in capability wrappers         |
| `src/tools/builtin/`          | Built-in tool wrappers               |
| `src/plugins/`                | Playground plugins                   |
| `src/plugins/loader.py`       | Plugin discovery from manifest.yaml  |
| `src/cli/main.py`             | Typer CLI entry point                |
| `src/api/routers/unified_ws.py` | Unified WebSocket endpoint         |

## Plugin Development

Create a directory under `src/plugins/<name>/` with:

```
manifest.yaml     # name, version, type, description, stages
capability.py     # class extending BaseCapability
```

Minimal `manifest.yaml`:
```yaml
name: my_plugin
version: 0.1.0
type: playground
description: "My custom plugin"
stages: [step1, step2]
```

Minimal `capability.py`:
```python
from src.core.capability_protocol import BaseCapability, CapabilityManifest
from src.core.context import UnifiedContext
from src.core.stream_bus import StreamBus

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

## Dependency Layers

```
requirements/core.txt       — CLI minimum (~80MB)
requirements/server.txt     — + FastAPI/uvicorn
requirements/rag-lite.txt   — + LlamaIndex RAG
requirements/rag-full.txt   — + raganything + docling
requirements/providers.txt  — + native LLM SDKs
requirements/dev.txt        — + test/lint tools
```
