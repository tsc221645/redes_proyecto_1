import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.llm.orchestrator import ChatOrchestrator
from backend.llm.provider import tool_schema


class FakeProvider:
    def __init__(self):
        self.calls = 0

    def complete(self, messages, tools):
        self.calls += 1
        if self.calls == 1:
            return {"choices": [{"message": {"role": "assistant", "content": None, "tool_calls": [{"id": "1", "function": {"name": "echo", "arguments": '{"text":"ok"}'}}]}}]}
        return {"choices": [{"message": {"role": "assistant", "content": "Final answer"}}]}


def test_orchestrator_executes_tool_and_returns_final_answer():
    provider = FakeProvider()
    result = ChatOrchestrator(provider, {"echo": lambda args: args["text"]}).run([], [tool_schema("echo", "Echo", {"type": "object"})])
    assert result == "Final answer"
    assert provider.calls == 2


def test_orchestrator_rejects_unknown_tool_safely():
    class UnknownProvider(FakeProvider):
        def complete(self, messages, tools):
            self.calls += 1
            return {"choices": [{"message": {"role": "assistant", "content": "done"}}]}
    assert ChatOrchestrator(UnknownProvider(), {}).run([], []) == "done"
