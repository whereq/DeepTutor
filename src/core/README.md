# Core Module

The Core module provides essential system services including configuration management, logging, and system initialization.

## 📋 Overview

The Core module is the foundation of the OpenTutor system, providing:
- Unified configuration management (environment variables + YAML)
- Comprehensive logging system
- System initialization and setup
- Path management utilities

## 🏗️ Architecture

```
core/
├── __init__.py
├── core.py                  # Configuration management
├── setup.py                 # System initialization
└── logging/                  # Logging system
    ├── __init__.py
    ├── logger.py            # Logger implementation
    ├── handlers.py         # Log handlers
    ├── llm_stats.py        # LLM usage statistics
    ├── log_forwarder.py    # Log forwarding
    ├── lightrag_forward.py # LightRAG log forwarding
    └── terminal_display.py # Terminal display utilities
```

## 🔧 Components

### core.py

**Configuration Management**

Provides unified configuration loading from environment variables and YAML files.

**Key Functions**:

#### `get_llm_config() -> dict`
Returns LLM configuration from environment variables:
```python
{
    "binding": "openai",
    "model": "gpt-4o",
    "api_key": "...",
    "base_url": "https://api.openai.com/v1"
}
```

#### `get_tts_config() -> dict`
Returns TTS configuration from environment variables:
```python
{
    "model": "sambert-zhichu-v1",
    "api_key": "...",
    "base_url": "https://dashscope.aliyuncs.com/api/v1",
    "voice": "Cherry"
}
```

#### `get_embedding_config() -> dict`
Returns embedding model configuration from environment variables.

#### `load_config_with_main(config_file: str, project_root: Path) -> dict`
Loads configuration from `main.yaml`:
1. Loads `config/main.yaml` as configuration
2. Returns the configuration dictionary

**Usage**:
```python
from src.core.core import load_config_with_main
from pathlib import Path

config = load_config_with_main("main.yaml", Path(__file__).parent.parent.parent)
```

#### `get_agent_params(module_name: str) -> dict`
Gets agent parameters (temperature, max_tokens) from `agents.yaml`:

**Usage**:
```python
from src.core.core import get_agent_params

params = get_agent_params("solve")
# Returns: {"temperature": 0.3, "max_tokens": 8192}
```

### setup.py

**System Initialization**

Handles system setup and initialization tasks.

**Key Functions**:

#### `init_user_directories(project_root: Optional[Path] = None) -> None`
Initializes all required user data directories:
- `data/user/solve/`
- `data/user/question/`
- `data/user/research/`
- `data/user/guide/`
- `data/user/notebook/`
- `data/user/co-writer/`
- `data/user/logs/`
- `data/user/run_code_workspace/`

#### `get_backend_port(project_root: Optional[Path] = None) -> int`
Gets backend port from configuration.

#### `get_frontend_port(project_root: Optional[Path] = None) -> int`
Gets frontend port from configuration.

### logging/

**Comprehensive Logging System**

#### logger.py

**Main Logger Implementation**

Provides `get_logger()` function for creating loggers:

```python
from src.core.logging import get_logger

logger = get_logger("MyModule", level="INFO", log_dir="./logs")
```

**Features**:
- File and console output
- Configurable log levels
- Automatic log rotation
- Module-specific loggers

#### llm_stats.py

**LLM Usage Statistics**

Tracks LLM API usage:
- Token counts (input/output)
- API calls
- Cost estimation

**Usage**:
```python
from src.core.logging import LLMStats

stats = LLMStats(module_name="MyModule")
stats.add_call(model="gpt-4o", system_prompt="...", user_prompt="...", response="...")
stats.print_summary()
```

#### log_forwarder.py

**Log Forwarding**

Forwards logs from external libraries (e.g., LightRAG) to the main logging system.

#### handlers.py

**Custom Log Handlers**

Custom handlers for file and console output.

## ⚙️ Configuration

### Environment Variables

Required in `.env` or `OpenTutor.env`:

```bash
# LLM Configuration
LLM_BINDING_API_KEY=your_api_key
LLM_BINDING_HOST=https://api.openai.com/v1
LLM_MODEL=gpt-4o

# TTS Configuration (optional)
TTS_API_KEY=your_tts_key
TTS_URL=https://dashscope.aliyuncs.com/api/v1
TTS_MODEL=sambert-zhichu-v1

# Embedding Configuration (optional)
EMBEDDING_BINDING_API_KEY=your_embedding_key
EMBEDDING_BINDING_HOST=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-large
```

### YAML Configuration

Configuration files in `config/`:
- `main.yaml` - Main system configuration
- `solve_config.yaml` - Solve module configuration
- `research_config.yaml` - Research module configuration
- etc.

## 📝 Usage Examples

### Loading Configuration

```python
from src.core.core import load_config_with_main
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
config = load_config_with_main("solve_config.yaml", project_root)

# Access configuration
output_dir = config.get('paths', {}).get('user_data_dir')
max_iterations = config.get('system', {}).get('max_analysis_iterations', 5)
```

### Getting LLM Config

```python
from src.core.core import get_llm_config

llm_config = get_llm_config()
api_key = llm_config["api_key"]
base_url = llm_config["base_url"]
model = llm_config["model"]
```

### Using Logger

```python
from src.core.logging import get_logger

logger = get_logger("MyModule", level="DEBUG")
logger.info("Information message")
logger.error("Error message")
```

### Tracking LLM Usage

```python
from src.core.logging import LLMStats

stats = LLMStats(module_name="MyModule")
# After LLM call
stats.add_call(
    model="gpt-4o",
    system_prompt="You are a helpful assistant.",
    user_prompt="What is AI?",
    response="AI is..."
)
# Print summary
stats.print_summary()
```

### Initializing System

```python
from src.core.setup import init_user_directories
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
init_user_directories(project_root)
```

## 🔗 Related Modules

- **Config Files**: `config/` - YAML configuration files
- **API**: `src/api/` - Uses core for configuration
- **Agents**: `src/agents/` - Use core for logging and config

## 🛠️ Development

### Adding New Configuration

1. Add to environment variables if it's a secret or API key
2. Add to `main.yaml` if it's a system-wide setting
3. Add to module config if it's module-specific
4. Update `core.py` if needed for loading

### Adding New Logger

```python
from src.core.logging import get_logger

logger = get_logger("NewModule", level="INFO", log_dir="./logs")
```

### Custom Log Handler

Extend `handlers.py` to add custom handlers.

## ⚠️ Notes

1. **Configuration Priority**: Environment variables override YAML config
2. **Path Resolution**: Always use `load_config_with_main()` for proper path resolution
3. **Logging**: Use module-specific loggers for better organization
4. **Statistics**: LLM stats are tracked per module
