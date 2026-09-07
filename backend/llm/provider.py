from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any, Dict, List, Protocol

from dotenv import load_dotenv


class LLMProvider(Protocol):
    def complete(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Any: ...


@dataclass
class LiteLLMProvider:
    """Provider-neutral adapter using LiteLLM's OpenAI-compatible interface."""

    model: str
    temperature: float = 0.0

    @classmethod
    def from_env(cls) -> "LiteLLMProvider":
        """Build the provider from `.env` without printing credentials."""
        load_dotenv()
        model = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
        provider = model.split("/", 1)[0].lower()
        key_names = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}
        key_name = key_names.get(provider)
        if key_name and not os.getenv(key_name):
            raise ValueError(f"Missing API key for configured LLM provider: {key_name}")
        return cls(model=model, temperature=float(os.getenv("LLM_TEMPERATURE", "0")))

    def complete(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Any:
        try:
            from litellm import completion
        except ImportError as exc:
            raise RuntimeError("litellm is required for LLM integration") from exc
        return completion(model=self.model, messages=messages, tools=tools, temperature=self.temperature)


def tool_schema(name: str, description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Convert an MCP tool definition to the function-tool format expected by LiteLLM."""
    return {"type": "function", "function": {"name": name, "description": description, "parameters": parameters}}
