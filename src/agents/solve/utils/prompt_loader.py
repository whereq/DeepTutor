#!/usr/bin/env python
"""
Prompt Loader - Unified Prompt loading and management system
Supports multi-language, version control, and caching
"""

from pathlib import Path
from typing import Any

import yaml


class PromptLoader:
    """Prompt loader - Load Prompt configuration from YAML files"""

    def __init__(self, base_dir: str | None = None, language: str = "zh"):
        """
        Initialize PromptLoader

        Args:
            base_dir: Base directory for Prompt config files (defaults to prompts directory of current module)
            language: Language code ('zh' | 'en')
        """
        if base_dir is None:
            base_dir = Path(__file__).parent.parent.parent.parent / "prompts"
        else:
            base_dir = Path(base_dir)

        self.base_dir = base_dir
        self.language = language
        self._cache = {}

    def set_language(self, language: str):
        """
        Set language

        Args:
            language: Language code ('zh' | 'en')
        """
        if language not in ["zh", "en"]:
            raise ValueError(f"Unsupported language: {language}, only 'zh' or 'en' supported")

        self.language = language
        # Clear cache because language changed
        self._cache.clear()

    def load(self, agent_name: str, version: str = "latest") -> dict[str, str]:
        """
        Load Prompt configuration for specified Agent

        Args:
            agent_name: Agent name (corresponds to YAML filename without extension)
            version: Version identifier (currently only 'latest' supported)

        Returns:
            {
                'system': str,          # System prompt (fully constructed)
                'user_template': str,   # User prompt template
                'output_format': str    # Output format description
            }

        Raises:
            FileNotFoundError: If corresponding YAML file not found
            ValueError: If YAML format is incorrect
        """
        cache_key = f"{agent_name}_{version}_{self.language}"

        # Check cache
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Build file path (supports subdirectory search)
        # First try direct path
        prompt_file = self.base_dir / self.language / f"{agent_name}.yaml"

        # If not exists, try searching in subdirectories
        if not prompt_file.exists():
            lang_dir = self.base_dir / self.language
            if lang_dir.exists():
                # Search in all subdirectories
                found_files = list(lang_dir.rglob(f"{agent_name}.yaml"))
                if found_files:
                    prompt_file = found_files[0]
                else:
                    raise FileNotFoundError(
                        f"Prompt config file not found: {agent_name}.yaml\n"
                        f"Please ensure file exists in {self.base_dir / self.language}/ or its subdirectories"
                    )
            else:
                raise FileNotFoundError(
                    f"Prompt config directory not found: {lang_dir}\nPlease ensure directory exists"
                )

        # Load YAML
        try:
            with open(prompt_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Failed to parse YAML file ({prompt_file}): {e!s}")

        # Validate configuration structure
        config_type = self._validate_config(config, agent_name)

        # Build Prompt
        prompts = self._build_prompts(config, config_type)

        # Cache result
        self._cache[cache_key] = prompts

        return prompts

    def _validate_config(self, config: dict[str, Any], agent_name: str) -> str:
        """
        Validate configuration structure integrity

        Args:
            config: Loaded configuration dictionary
            agent_name: Agent name (for error messages)

        Raises:
            ValueError: If configuration structure is incorrect
        """
        if "system" not in config:
            raise ValueError(f"[{agent_name}] missing 'system' configuration section")

        system_section = config["system"]

        if isinstance(system_section, dict):
            if "user" not in config:
                raise ValueError(f"[{agent_name}] missing 'user' configuration section")

            required_system_fields = ["role", "task"]
            for field in required_system_fields:
                if field not in system_section:
                    raise ValueError(
                        f"[{agent_name}] 'system' configuration section missing '{field}' field"
                    )

            user_config = config["user"]
            if "template" not in user_config:
                raise ValueError(
                    f"[{agent_name}] 'user' configuration section missing 'template' field"
                )

            return "structured"

        if not isinstance(system_section, str):
            raise ValueError(f"[{agent_name}] 'system' must be a string or object")

        if "user_template" not in config:
            raise ValueError(f"[{agent_name}] raw format missing 'user_template'")

        if not isinstance(config["user_template"], str):
            raise ValueError(f"[{agent_name}] 'user_template' must be a string")

        return "raw"

    def _build_prompts(self, config: dict[str, Any], config_type: str) -> dict[str, str]:
        """
        Build complete Prompt from configuration

        Args:
            config: Loaded configuration dictionary

        Returns:
            {
                'system': str,
                'user_template': str,
                'output_format': str
            }
        """
        if config_type == "structured":
            system_config = config["system"]
            user_config = config["user"]

            system_parts = []
            system_parts.append(f"You are {system_config['role']}.")
            system_parts.append("")
            system_parts.append(system_config["task"])

            if system_config.get("requirements"):
                system_parts.append("")
                system_parts.append("Requirements:")
                for req in system_config["requirements"]:
                    system_parts.append(f"- {req}")

            if system_config.get("constraints"):
                system_parts.append("")
                system_parts.append("Constraints:")
                for cons in system_config["constraints"]:
                    system_parts.append(f"- {cons}")

            output_format = ""
            if system_config.get("output_format"):
                system_parts.append("")
                system_parts.append("Output Format:")
                system_parts.append(system_config["output_format"])
                output_format = system_config["output_format"]

            if system_config.get("notes"):
                system_parts.append("")
                system_parts.append("Notes:")
                for note in system_config["notes"]:
                    system_parts.append(f"- {note}")

            system_prompt = "\n".join(system_parts)
            user_template = user_config["template"]

            return {
                "system": system_prompt,
                "user_template": user_template,
                "output_format": output_format,
            }

        prompts = {"system": config["system"], "user_template": config.get("user_template", "")}

        for key, value in config.items():
            if key in ["system", "user_template"]:
                continue
            prompts[key] = value

        return prompts

    def list_available_prompts(self, language: str | None = None) -> list:
        """
        List available prompt configuration files for specified language

        Args:
            language: Language code (None uses current language)

        Returns:
            List of available agent names
        """
        lang = language or self.language
        prompts_dir = self.base_dir / lang

        if not prompts_dir.exists():
            return []

        # Get all YAML files
        yaml_files = list(prompts_dir.glob("*.yaml"))

        # Extract filenames (without extension)
        agent_names = [f.stem for f in yaml_files]

        return sorted(agent_names)

    def clear_cache(self):
        """Clear cache"""
        self._cache.clear()

    def reload(self, agent_name: str, version: str = "latest") -> dict[str, str]:
        """
        Force reload prompt configuration (ignore cache)

        Args:
            agent_name: Agent name
            version: Version identifier

        Returns:
            Prompt configuration
        """
        cache_key = f"{agent_name}_{version}_{self.language}"

        # Delete cache
        if cache_key in self._cache:
            del self._cache[cache_key]

        # Reload
        return self.load(agent_name, version)


# Global PromptLoader instance (singleton pattern)
_global_loader = None


def get_prompt_loader(language: str | None = None) -> PromptLoader:
    """
    Get global PromptLoader instance

    Args:
        language: Language code (None uses 'zh')

    Returns:
        PromptLoader instance
    """
    global _global_loader

    if _global_loader is None:
        lang = language or "zh"
        _global_loader = PromptLoader(language=lang)
    elif language is not None:
        _global_loader.set_language(language)

    return _global_loader


if __name__ == "__main__":
    # Test PromptLoader
    print("PromptLoader Test")
    print("=" * 60)

    # Create loader
    loader = PromptLoader(language="zh")

    # List available prompts
    available = loader.list_available_prompts()
    print(f"Available Prompt configurations: {available}")
    print()

    # If available configurations exist, load first one for testing
    if available:
        test_agent = available[0]
        print(f"Testing load: {test_agent}")
        try:
            prompts = loader.load(test_agent)
            print("✅ Load successful")
            print(f"System Prompt (first 200 chars):\n{prompts['system'][:200]}...")
            print(f"\nUser Template (first 200 chars):\n{prompts['user_template'][:200]}...")
        except Exception as e:
            print(f"❌ Load failed: {e!s}")
    else:
        print("Hint: No available Prompt configuration files")
        print("Please create YAML configuration files in prompts/zh/ directory")
