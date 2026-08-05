from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Mapping

from .provider import LLMProvider


class ChatOrchestrator:
    """Coordinate an LLM with MCP tools while bounding tool-call loops."""

    def __init__(self, provider: LLMProvider, tools: Mapping[str, Any], *, tool_schemas: List[Dict[str, Any]] | None = None, max_tool_rounds: int = 4) -> None:
        self.provider = provider
        self.tools = dict(tools)
        self.tool_schemas = tool_schemas or []
        self.max_tool_rounds = max_tool_rounds
        self.last_conversation: List[Dict[str, Any]] = []

    def run(self, messages: List[Dict[str, Any]], tool_schemas: List[Dict[str, Any]] | None = None) -> str:
        tool_schemas = self.tool_schemas if tool_schemas is None else tool_schemas
        conversation = list(messages)
        for _ in range(self.max_tool_rounds):
            response = self.provider.complete(conversation, tool_schemas)
            message = self._message(response)
            tool_calls = self._value(message, "tool_calls", [])
            if not tool_calls:
                conversation.append(message)
                self.last_conversation = conversation
                return self._value(message, "content", "") or ""
            conversation.append(message)
            for call in tool_calls:
                name = self._value(self._value(call, "function", {}), "name", "")
                raw_arguments = self._value(self._value(call, "function", {}), "arguments", "{}")
                if name not in self.tools:
                    result = {"error": f"Unknown tool: {name}"}
                else:
                    try:
                        parsed_arguments = json.loads(raw_arguments) if isinstance(raw_arguments, str) else raw_arguments
                        if os.getenv("LLM_DEBUG", "false").lower() == "true":
                            print(f"[LLM_DEBUG] tool={name} arguments={parsed_arguments}", file=sys.stderr, flush=True)
                        result = self.tools[name](parsed_arguments)
                    except (ValueError, TypeError, RuntimeError, json.JSONDecodeError) as exc:
                        result = {"error": str(exc)}
                        if os.getenv("LLM_DEBUG", "false").lower() == "true":
                            print(f"[LLM_DEBUG] tool_error={exc}", file=sys.stderr, flush=True)
                conversation.append({
                    "role": "tool",
                    "tool_call_id": self._value(call, "id", ""),
                    "name": name,
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                })
        raise RuntimeError("Maximum tool-call rounds exceeded")

    @staticmethod
    def _message(response: Any) -> Any:
        choices = response.choices if hasattr(response, "choices") else response["choices"]
        choice = choices[0]
        return choice.get("message") if isinstance(choice, dict) else choice.message

    @staticmethod
    def _value(value: Any, key: str, default: Any) -> Any:
        if isinstance(value, dict):
            return value.get(key, default)
        return getattr(value, key, default)
