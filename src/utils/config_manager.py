import os
from pathlib import Path
from threading import Lock
from typing import Any, Dict

import yaml


class ConfigManager:
    """
    Thread-safe manager for reading and writing configuration files.
    Primarily manages config/main.yaml and reads .env.
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ConfigManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.project_root = Path(__file__).parent.parent.parent
        self.config_path = self.project_root / "config" / "main.yaml"
        self._config_cache = None
        self._last_mtime = 0
        self._initialized = True

    def load_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load configuration from main.yaml.
        Uses caching based on file modification time.
        """
        if not self.config_path.exists():
            return {}

        current_mtime = self.config_path.stat().st_mtime

        if self._config_cache is None or force_reload or current_mtime > self._last_mtime:
            with self._lock:
                try:
                    with open(self.config_path, "r", encoding="utf-8") as f:
                        self._config_cache = yaml.safe_load(f) or {}
                    self._last_mtime = current_mtime
                except Exception as e:
                    print(f"Error loading config: {e}")
                    return {}

        return self._config_cache.copy()  # Return copy to prevent direct mutation

    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration to main.yaml.
        Merges provided config with existing one to ensure partial updates work if needed,
        though usually we expect full section replacements.
        """
        try:
            # First, load current to ensure we have latest structure
            current_config = self.load_config(force_reload=True)

            # recursive update strategy could be implemented here if granular updates are needed,
            # but for now we expect the caller to provide structurally correct data or we just save what's given.
            # To be safe against partial updates killing unrelated sections, we should assume 'config'
            # might just contain the sections to update.

            # Simple recursive update helper
            def deep_update(target, source):
                for key, value in source.items():
                    if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                        deep_update(target[key], value)
                    else:
                        target[key] = value

            deep_update(current_config, config)

            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with self._lock:
                with open(self.config_path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(
                        current_config,
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                        sort_keys=False,
                    )

                # Update cache
                self._config_cache = current_config
                self._last_mtime = self.config_path.stat().st_mtime

            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_env_info(self) -> Dict[str, str]:
        """
        Read relevant environment variables.
        """
        # Reload env vars from file could be done here using python-dotenv if needed,
        # but usually os.environ is populated at startup.
        # For dynamic .env reading, we might want to read the file directly.

        env_vars = {}
        env_path = self.project_root / ".env"

        if env_path.exists():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            key, val = line.split("=", 1)
                            env_vars[key.strip()] = val.strip().strip('"').strip("'")
            except Exception:
                pass

        # Fallback to os.environ for values not in .env file but set in environment
        # Specific keys we care about
        keys_of_interest = ["LLM_MODEL", "OPENAI_API_KEY", "GOOGLE_API_KEY"]  # Add others as needed

        # We might want to mask keys, but returning model name is safe.
        return {
            "model": env_vars.get("LLM_MODEL", os.environ.get("LLM_MODEL", "Pro/Flash")),
            # Add other non-sensitive info if needed
        }
