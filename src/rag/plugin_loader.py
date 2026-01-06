"""
RAG Plugin Loader
Automatically discovers and loads RAG plugins from the plugins directory.
"""

import importlib
import sys
from pathlib import Path
from typing import Dict, List, Callable, Any
import logging

logger = logging.getLogger(__name__)


class PluginLoader:
    """Discovers and manages RAG plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, Dict[str, Any]] = {}
        self._load_plugins()
    
    def _load_plugins(self):
        """Auto-discover all plugins in plugins/ folder"""
        plugins_dir = Path(__file__).parent / "plugins"
        
        if not plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {plugins_dir}")
            return
        
        # Find all Python files in plugins directory
        for plugin_file in plugins_dir.glob("*.py"):
            # Skip private files and template
            if plugin_file.stem.startswith("_"):
                continue
            
            try:
                # Import plugin module
                module_name = f"src.rag.plugins.{plugin_file.stem}"
                module = importlib.import_module(module_name)
                
                # Verify it has required functions
                required_functions = ["initialize_rag", "search_rag", "delete_rag"]
                missing = [func for func in required_functions if not hasattr(module, func)]
                
                if missing:
                    logger.warning(
                        f"Plugin {plugin_file.stem} missing required functions: {missing}"
                    )
                    continue
                
                # Load plugin metadata
                config = getattr(module, "CONFIG", {})
                plugin_name = config.get("name", plugin_file.stem)
                
                # Store plugin
                self.plugins[plugin_file.stem] = {
                    "module": module,
                    "config": config,
                    "initialize": module.initialize_rag,
                    "search": module.search_rag,
                    "delete": module.delete_rag,
                    "name": plugin_name,
                }
                
                logger.info(f"✅ Loaded RAG plugin: {plugin_file.stem} ({plugin_name})")
                
            except Exception as e:
                logger.error(f"❌ Failed to load plugin {plugin_file.stem}: {e}")
    
    def get_plugin(self, name: str) -> Dict[str, Any]:
        """
        Get plugin by name.
        
        Args:
            name: Plugin identifier (filename without .py)
        
        Returns:
            Dictionary with plugin functions and metadata
        
        Raises:
            ValueError: If plugin not found
        """
        if name not in self.plugins:
            available = list(self.plugins.keys())
            raise ValueError(
                f"RAG plugin '{name}' not found. "
                f"Available plugins: {available}"
            )
        return self.plugins[name]
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all available plugins with their metadata.
        
        Returns:
            List of plugin information dictionaries
        """
        return [
            {
                "id": plugin_id,
                "name": plugin["config"].get("name", plugin_id),
                "version": plugin["config"].get("version", "unknown"),
                "description": plugin["config"].get("description", ""),
                "author": plugin["config"].get("author", ""),
                "supported_modes": plugin["config"].get("supported_modes", []),
                "requires": plugin["config"].get("requires", []),
            }
            for plugin_id, plugin in self.plugins.items()
        ]
    
    def has_plugin(self, name: str) -> bool:
        """Check if a plugin is available"""
        return name in self.plugins
    
    def reload_plugins(self):
        """Reload all plugins (useful for development)"""
        self.plugins.clear()
        self._load_plugins()


# Global loader instance
_loader = None


def get_loader() -> PluginLoader:
    """Get the global plugin loader instance"""
    global _loader
    if _loader is None:
        _loader = PluginLoader()
    return _loader


def get_plugin(name: str) -> Dict[str, Any]:
    """
    Get a RAG plugin by name.
    
    Args:
        name: Plugin identifier
    
    Returns:
        Plugin dictionary with functions
    """
    return get_loader().get_plugin(name)


def list_plugins() -> List[Dict[str, Any]]:
    """
    List all available RAG plugins.
    
    Returns:
        List of plugin metadata
    """
    return get_loader().list_plugins()


def has_plugin(name: str) -> bool:
    """Check if a plugin exists"""
    return get_loader().has_plugin(name)


def reload_plugins():
    """Reload all plugins"""
    get_loader().reload_plugins()
