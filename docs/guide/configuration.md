# Configuration

DeepTutor uses YAML configuration files for easy customization.

## 📁 Configuration Files

```
config/
├── main.yaml              # Main system configuration (all module settings)
├── agents.yaml            # Unified agent parameters (temperature, max_tokens)
└── README.md              # Full documentation
```

| File | Purpose |
|------|---------|
| `config/main.yaml` | Server ports, paths, tools, module settings |
| `config/agents.yaml` | LLM parameters for each agent module |
| `.env` | API keys and secrets |

## 🔧 Server Configuration

Edit `config/main.yaml`:

```yaml
server:
  backend_port: 8001
  frontend_port: 3782

system:
  language: en  # "zh" or "en"
```

## 🤖 Agent LLM Configuration

Each module has unified LLM settings in `config/agents.yaml`:

```yaml
# Solve Module - Problem solving agents
solve:
  temperature: 0.3
  max_tokens: 8192

# Research Module - Deep research agents
research:
  temperature: 0.5
  max_tokens: 12000

# Question Module - Question generation agents
question:
  temperature: 0.7
  max_tokens: 4096

# Guide Module - Learning guidance agents
guide:
  temperature: 0.5
  max_tokens: 8192

# IdeaGen Module - Idea generation agents
ideagen:
  temperature: 0.7
  max_tokens: 4096

# CoWriter Module - Collaborative writing agents
co_writer:
  temperature: 0.7
  max_tokens: 4096
```

## 🔑 Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# ============================================================================
# LLM (Large Language Model) Configuration - Required
# ============================================================================
LLM_BINDING=openai                        # Options: openai, azure_openai, ollama
LLM_MODEL=gpt-4o                          # e.g., gpt-4o, deepseek-chat, qwen-plus
LLM_HOST=https://api.openai.com/v1
LLM_API_KEY=your_api_key

# ============================================================================
# Embedding Model Configuration - Required for Knowledge Base
# ============================================================================
EMBEDDING_BINDING=openai
EMBEDDING_MODEL=text-embedding-3-large    # e.g., text-embedding-3-large, text-embedding-3-small
EMBEDDING_DIM=3072                        # Important !! Must match model dimensions
EMBEDDING_HOST=https://api.openai.com/v1
EMBEDDING_API_KEY=your_api_key

# ============================================================================
# Optional Features
# ============================================================================
# Web Search (Perplexity API)
PERPLEXITY_API_KEY=your_perplexity_key

# TTS (Text-to-Speech) for Co-Writer narration
TTS_MODEL=
TTS_URL=
TTS_API_KEY=
```

> **Note**: Please make sure you have configured the right dimensions. Currently our RAG module uses RAG-Anything, you could further check [its repo](https://github.com/HKUDS/RAG-Anything) for more questions.

## 🛠️ Tool Configuration

Configure tool availability in `config/main.yaml`:

```yaml
tools:
  rag_tool:
    kb_base_dir: ./data/knowledge_bases
    default_kb: ai_textbook
  run_code:
    workspace: ./data/user/run_code_workspace
  web_search:
    enabled: true  # Global switch for web search
  query_item:
    enabled: true
    max_results: 5
```

## 📂 Data Storage

All user content and system data are stored in the `data/` directory:

```
data/
├── knowledge_bases/              # Knowledge base storage
└── user/                         # User activity data
    ├── solve/                    # Problem solving results
    ├── question/                 # Generated questions
    ├── research/                 # Research reports and cache
    ├── co-writer/                # Interactive IdeaGen documents
    ├── notebook/                 # Notebook records
    ├── guide/                    # Guided learning sessions
    ├── logs/                     # System logs
    └── run_code_workspace/       # Code execution workspace
```

## 🔗 Advanced Configuration

For the full configuration reference, see [config/README.md](https://github.com/HKUDS/DeepTutor/tree/main/config).
