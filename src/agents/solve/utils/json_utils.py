#!/usr/bin/env python
"""
JSON Utils - JSON parsing utilities
Specifically for extracting and parsing JSON data from LLM output, supports Markdown code block processing
"""

import json
import re
from typing import Any


def extract_json_from_text(text: str) -> dict[str, Any] | list[Any] | None:
    """
    Extract JSON object or array from text

    Supports the following formats:
    1. Code blocks wrapped in ```json ... ```
    2. Code blocks wrapped in ``` ... ```
    3. Pure JSON text

    Args:
        text: Original text containing JSON

    Returns:
        Parsed JSON object (dict) or array (list), returns None if parsing fails
    """
    if not text:
        return None

    # 1. Try matching Markdown code blocks
    # Match ```json {...} ``` or ``` {...} ```
    code_block_pattern = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```")
    match = code_block_pattern.search(text)

    if match:
        json_str = match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # If parsing fails in code block, may contain comments or illegal characters, try cleaning
            # Can add more complex cleaning logic here, currently keep original and try next method
            pass

    # 2. If no code block or code block parsing failed, try finding JSON structure in entire text
    # Find outermost {...} or [...]

    # Remove possible comments // ... or # ... (simple handling)
    # Note: This may mistakenly delete content in URLs or strings, use with caution.
    # Do not aggressively remove comments, rely on LLM output standards.

    # Find first { or [
    start_idx = -1
    stack = []

    # Scan for valid JSON start and end
    # This is a simplified search, assuming JSON is the main part of the text

    try:
        # Try direct parsing
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Use regex to find outermost {} or []
    # dotall mode
    json_obj_pattern = re.compile(r"\{[\s\S]*\}")
    json_arr_pattern = re.compile(r"\[[\s\S]*\]")

    # Prefer finding object
    match_obj = json_obj_pattern.search(text)
    if match_obj:
        try:
            return json.loads(match_obj.group(0))
        except json.JSONDecodeError:
            pass

    # Find array
    match_arr = json_arr_pattern.search(text)
    if match_arr:
        try:
            return json.loads(match_arr.group(0))
        except json.JSONDecodeError:
            pass

    # 3. Try fixing common LLM JSON errors (e.g., trailing commas)
    # This is a relatively complex task, can use specialized libraries like json_repair,
    # but to avoid introducing new dependencies, do simple string processing here

    return None


def clean_json_string(json_str: str) -> str:
    """
    Clean JSON string, remove common illegal characters
    """
    # Remove control characters
    json_str = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", json_str)
    return json_str
