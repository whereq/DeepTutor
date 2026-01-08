import os
from typing import Callable, List, Optional

import aiohttp
from lightrag.llm.openai import openai_complete_if_cache


class LLMFactory:
    """
    Factory for creating LLM completion functions for various providers.
    Provides a unified interface for calling different LLM APIs.
    """

    @staticmethod
    async def anthropic_complete(
        model: str,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Wrapper for Anthropic (Claude) API.
        """
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key is missing.")

        # Default Anthropic API URL if not provided
        if not base_url:
            url = "https://api.anthropic.com/v1/messages"
        else:
            url = base_url.rstrip("/")
            if not url.endswith("/messages"):
                url += "/messages"

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        data = {
            "model": model,
            "system": system_prompt,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", 4096),
            "temperature": kwargs.get("temperature", 0.7),
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API error: {response.status} - {error_text}")

                result = await response.json()
                # Anthropic returns a list of content blocks
                return result["content"][0]["text"]

    @staticmethod
    def get_completion_function(binding: str) -> Callable:
        """
        Returns the appropriate completion function based on the provider binding.
        """
        binding = binding.lower()

        if binding == "anthropic" or binding == "claude":
            return LLMFactory.anthropic_complete

        # For ollama-cloud, we usually treat it as OpenAI compatible or use a specific endpoint
        # If it's just a hosted Ollama, it's often OpenAI compatible (/v1)
        if binding == "ollama-cloud":
            # For now, treat it as OpenAI compatible
            return openai_complete_if_cache

        # Default to OpenAI-compatible for most (openai, azure_openai, ollama local, openrouter, deepseek, gemini)
        return openai_complete_if_cache

    @staticmethod
    async def fetch_models(binding: str, base_url: str, api_key: Optional[str] = None) -> List[str]:
        """
        Fetch available models from the provider.
        """
        binding = binding.lower()
        base_url = base_url.rstrip("/")

        headers = {}
        if api_key:
            if binding in ["anthropic", "claude"]:
                headers["x-api-key"] = api_key
            else:
                headers["Authorization"] = f"Bearer {api_key}"

        async with aiohttp.ClientSession() as session:
            try:
                # Strategy 1: Local Ollama /api/tags
                # Try this for anything that looks like local Ollama or specifically has 'ollama' in binding/url
                # but NOT if it's explicitly 'ollama.com' (cloud) unless it's a fallback
                is_likely_local_ollama = (
                    (binding == "ollama" or "ollama" in base_url.lower())
                    and "ollama.com" not in base_url.lower()
                    or ":11434" in base_url
                )

                if is_likely_local_ollama:
                    url = base_url.rstrip("/").replace("/v1", "") + "/api/tags"
                    try:
                        async with session.get(url, headers=headers) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                if "models" in data:
                                    return [m["name"] for m in data.get("models", [])]
                    except Exception:
                        pass  # Try Strategy 2 if this fails

                # Strategy 2: Standard OpenAI /models (also used by Ollama Cloud)
                url = f"{base_url.rstrip('/')}/models"
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Handle standard OpenAI format: {"data": [{"id": "model-id"}, ...]}
                        if "data" in data and isinstance(data["data"], list):
                            return [
                                m.get("id") or m.get("name")
                                for m in data["data"]
                                if m.get("id") or m.get("name")
                            ]
                        # Handle some providers that use {"models": ["model1", ...]}
                        elif "models" in data and isinstance(data["models"], list):
                            if data["models"] and isinstance(data["models"][0], dict):
                                return [
                                    m.get("id") or m.get("name")
                                    for m in data["models"]
                                    if m.get("id") or m.get("name")
                                ]
                            else:
                                return [str(m) for m in data["models"]]
                        # Handle raw list response
                        elif isinstance(data, list):
                            if data and isinstance(data[0], dict):
                                return [
                                    m.get("id") or m.get("name")
                                    for m in data
                                    if m.get("id") or m.get("name")
                                ]
                            else:
                                return [str(m) for m in data]

                # Fallback Strategy: If it's ollama.com but /models failed, try /api/tags as well
                if "ollama.com" in base_url:
                    url = base_url.rstrip("/").replace("/v1", "") + "/api/tags"
                    try:
                        async with session.get(url, headers=headers) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                return [m["name"] for m in data.get("models", [])]
                    except Exception:
                        pass

                return []
            except Exception as e:
                print(f"Error fetching models from {base_url}: {e}")
                return []


# Unified interface for agents
def sanitize_url(base_url: str, model: str = "") -> str:
    """
    Sanitize base URL for OpenAI-compatible APIs, with special handling for Ollama.
    """
    if not base_url:
        return base_url

    url = base_url.rstrip("/")

    # Ensure URL has a protocol (default to http for local/ollama)
    if url and not url.startswith(("http://", "https://")):
        url = "http://" + url

    # Standard OpenAI client library is strict about URLs:
    # - No trailing slashes
    # - No /chat/completions or /completions/messages/embeddings suffixes (it adds these automatically)
    for suffix in ["/chat/completions", "/completions", "/messages", "/embeddings"]:
        if url.endswith(suffix):
            url = url[: -len(suffix)]
            url = url.rstrip("/")

    # Special handling for Ollama: local/self-hosted Ollama requires /v1
    # for OpenAI compatibility. If it's port 11434 or has 'ollama' in URL
    # and it's not the cloud version (ollama.com), ensure it ends in /v1.
    if ":11434" in url or ("ollama" in url.lower() and "ollama.com" not in url.lower()):
        if not url.endswith("/v1"):
            url = url.rstrip("/") + "/v1"

    return url


async def llm_complete(
    model: str,
    prompt: str,
    system_prompt: str = "You are a helpful assistant.",
    binding: str = "openai",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Call the appropriate LLM provider based on binding.
    Includes a direct aiohttp fallback for reasoning models and OpenAI-compatible services.
    """
    complete_fn = LLMFactory.get_completion_function(binding)

    # Sanitize base_url for OpenAI-compatible endpoints
    # The OpenAI client library is strict about URLs:
    # - No trailing slashes
    # - No /chat/completions or /completions suffixes (it adds these automatically)
    if base_url and (complete_fn == openai_complete_if_cache or binding in ["openai", "ollama"]):
        original_url = base_url
        base_url = sanitize_url(base_url, model)

        if original_url != base_url:
            print(f"🔧 URL Sanitized: {original_url} -> {base_url}")
        print(f"🚀 LLM Call: model={model}, binding={binding}, base_url={base_url}")

    try:
        # 1. Attempt using standard driver
        if complete_fn == openai_complete_if_cache:
            response = await complete_fn(
                model=model,
                prompt=prompt,
                system_prompt=system_prompt,
                api_key=api_key,
                base_url=base_url,
                **kwargs,
            )
        else:
            response = await complete_fn(
                model=model,
                prompt=prompt,
                system_prompt=system_prompt,
                api_key=api_key,
                base_url=base_url,
                **kwargs,
            )

        # If response is empty, it might be a reasoning model that lightrag can't parse
        if not response:
            raise ValueError("Empty response from standard driver")

        return response

    except Exception as e:
        # 2. Fallback to direct aiohttp call for OpenAI-compatible bindings
        # This is useful for reasoning models (DeepSeek R1, Kimi) that might
        # return empty content but have reasoning in other fields.
        is_openai_compatible = binding.lower() in [
            "openai",
            "ollama",
            "ollama-cloud",
            "deepseek",
            "openrouter",
            "gemini",
        ]

        if is_openai_compatible and base_url:
            try:
                url = base_url.rstrip("/")
                if not url.endswith("/chat/completions"):
                    url += "/chat/completions"

                print(f"🔄 Fallback Direct Call: {url}")

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}" if api_key else "",
                }

                data = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_tokens": kwargs.get("max_tokens", 4096),
                }

                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=data) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            if "choices" in result and result["choices"]:
                                msg = result["choices"][0].get("message", {})
                                content = msg.get("content", "")

                                # If content is empty, look for reasoning/thinking fields
                                if not content:
                                    content = (
                                        msg.get("reasoning_content")
                                        or msg.get("reasoning")
                                        or msg.get("thought")
                                        or ""
                                    )

                                if content:
                                    return content
                        else:
                            error_text = await resp.text()
                            print(
                                f"❌ Fallback call failed with status={resp.status}: {error_text}"
                            )
            except Exception as e2:
                print(f"❌ Fallback direct call failed: {e2}")

        # If fallback also fails or isn't applicable, re-raise original
        raise e


async def llm_fetch_models(binding: str, base_url: str, api_key: Optional[str] = None) -> List[str]:
    """
    Fetch available models from the provider.
    """
    return await LLMFactory.fetch_models(binding, base_url, api_key)
