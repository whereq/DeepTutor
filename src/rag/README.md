# RAG Plugin System

A flexible, plugin-based RAG system that allows easy switching between different RAG implementations.

## 🎯 Quick Start

### Using the Default RAG (LightRAG)

```python
from src.tools.rag_tool import rag_search

# Search with default provider (from .env)
result = await rag_search(
    query="What is machine learning?",
    kb_name="my_textbook",
    mode="hybrid"
)
```

### Switching RAG Providers

**Option 1: Change `.env` file** (affects all users)
```bash
# .env
RAG_PROVIDER=lightrag  # or chromadb, pinecone, etc.
```

**Option 2: Override per request** (temporary)
```python
result = await rag_search(
    query="What is ML?",
    kb_name="textbook",
    provider="chromadb"  # Override default
)
```

## 📦 Available Plugins

| Plugin | Description | Modes | Best For |
|--------|-------------|-------|----------|
| **lightrag** | Graph-based RAG with entity extraction | hybrid, local, global, naive | Complex queries, relationships |

## 🔌 Creating a New Plugin

### Step 1: Copy the Template

```bash
cp src/rag/plugins/_template.py src/rag/plugins/my_rag.py
```

### Step 2: Implement 3 Functions

```python
async def initialize_rag(kb_name: str, documents: List[str]) -> bool:
    """Process and store documents"""
    # Your initialization code
    return True

async def search_rag(query: str, kb_name: str, mode: str = "hybrid") -> Dict:
    """Search for information"""
    # Your search code
    return {
        "content": "results here",
        "mode": mode,
        "provider": "my_rag"
    }

async def delete_rag(kb_name: str) -> bool:
    """Delete knowledge base"""
    # Your cleanup code
    return True

# Optional: Metadata
CONFIG = {
    "name": "My RAG",
    "description": "What this RAG does",
    "supported_modes": ["vector", "hybrid"],
}
```

### Step 3: That's It!

Your plugin is automatically discovered. No registration needed!

```python
# Use your new plugin
result = await rag_search(
    query="Test",
    kb_name="kb",
    provider="my_rag"  # Your plugin name (filename without .py)
)
```

## 🛠️ Plugin API Reference

### Functions Required

All plugins must implement these 3 async functions:

#### `initialize_rag(kb_name, documents) -> bool`
Initialize the RAG system with documents.
- **kb_name**: Name of the knowledge base
- **documents**: List of document contents
- **Returns**: True if successful

#### `search_rag(query, kb_name, mode) -> dict`
Search for relevant information.
- **query**: Search query string
- **kb_name**: Knowledge base to search
- **mode**: Search mode (provider-specific)
- **Returns**: Dict with `content`, `mode`, and `provider` keys

#### `delete_rag(kb_name) -> bool`
Delete a knowledge base.
- **kb_name**: Knowledge base to delete
- **Returns**: True if successful

### CONFIG Dictionary (Optional)

```python
CONFIG = {
    "name": str,              # Display name
    "version": str,           # Version number
    "author": str,            # Author name
    "description": str,       # Brief description
    "supported_modes": list,  # List of mode strings
    "requires": list,         # Python dependencies
}
```

## 📚 Usage Examples

### List Available Providers

```python
from src.tools.rag_tool import get_available_providers

providers = get_available_providers()
for p in providers:
    print(f"{p['id']}: {p['description']}")
```

### Initialize a Knowledge Base

```python
from src.tools.rag_tool import initialize_rag

documents = ["Doc 1 content", "Doc 2 content"]
success = await initialize_rag("my_kb", documents, provider="lightrag")
```

### Delete a Knowledge Base

```python
from src.tools.rag_tool import delete_rag

success = await delete_rag("old_kb")
```

## 🎨 Example Plugins

### Simple Vector Search (ChromaDB)

```python
"""ChromaDB Plugin - Simple vector search"""
import chromadb

_client = chromadb.Client()

async def initialize_rag(kb_name: str, documents: list) -> bool:
    collection = _client.create_collection(kb_name)
    collection.add(
        documents=documents,
        ids=[f"doc_{i}" for i in range(len(documents))]
    )
    return True

async def search_rag(query: str, kb_name: str, mode: str = "hybrid") -> dict:
    collection = _client.get_collection(kb_name)
    results = collection.query(query_texts=[query], n_results=5)
    return {
        "content": "\n\n".join(results['documents'][0]),
        "provider": "chromadb"
    }

async def delete_rag(kb_name: str) -> bool:
    _client.delete_collection(kb_name)
    return True

CONFIG = {
    "name": "ChromaDB",
    "description": "Fast vector search",
    "supported_modes": ["vector"],
}
```

Save as `src/rag/plugins/chromadb.py` and it's ready to use!

## 🔧 Advanced Features

### Per-Knowledge-Base Provider

```python
# KB 1 uses LightRAG (complex, graph-based)
result1 = await rag_search("complex query", "textbook", provider="lightrag")

# KB 2 uses ChromaDB (simple, fast)
result2 = await rag_search("simple query", "notes", provider="chromadb")
```

### Error Handling

```python
from src.rag.plugin_loader import has_plugin

if has_plugin("my_rag"):
    result = await rag_search(query, kb, provider="my_rag")
else:
    print("Plugin not available")
```

### Reload Plugins (Development)

```python
from src.rag.plugin_loader import reload_plugins

# After modifying a plugin
reload_plugins()
```

## 🚀 Benefits

✅ **No Vendor Lock-in**: Switch RAG systems anytime  
✅ **Easy to Extend**: Drop a file, it works  
✅ **Community Friendly**: Anyone can contribute plugins  
✅ **Flexible**: Each KB can use different RAG  
✅ **Simple**: No inheritance, just functions

## 📁 Directory Structure

```
src/
└── rag/
    ├── __init__.py
    ├── plugin_loader.py          # Auto-discovery engine
    └── plugins/
        ├── __init__.py
        ├── _template.py          # Copy this to start
        ├── lightrag.py           # Built-in: LightRAG
        └── your_plugin.py        # Drop your plugin here!
```

## 🤝 Contributing Plugins

Want to add a new RAG system? Just:

1. Copy `_template.py`
2. Fill in 3 functions
3. Submit PR

That's it! No complex registration or factory patterns needed.

## 📝 License

Same as DeepTutor project license.
