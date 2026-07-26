from __future__ import annotations

import json
import queue
import subprocess
import sys
import threading
from typing import Any, Dict, List, Sequence


class StdioTransport:
    """Transport that communicates with a line-delimited JSON-RPC subprocess."""

    def __init__(self, command: Sequence[str], *, timeout: float = 10.0, cwd: str | None = None) -> None:
        self.command = list(command)
        self.timeout = timeout
        self.cwd = cwd
        self.process: subprocess.Popen[str] | None = None
        self._responses: queue.Queue[Dict[str, Any]] = queue.Queue()
        self._stderr: queue.Queue[str] = queue.Queue()
        self._reader_thread: threading.Thread | None = None
        self._stderr_thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the server process and begin draining stdout/stderr."""
        if self.is_running:
            return
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
            cwd=self.cwd,
        )
        self._reader_thread = threading.Thread(target=self._read_stdout, daemon=True)
        self._stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
        self._reader_thread.start()
        self._stderr_thread.start()

    @property
    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def send(self, message: Dict[str, Any]) -> Dict[str, Any] | None:
        """Send one message and wait for its response; notifications return None."""
        if not self.is_running:
            details = "; ".join(self.stderr_lines())
            suffix = f": {details}" if details else ""
            raise RuntimeError(f"stdio server is not running{suffix}")
        assert self.process is not None and self.process.stdin is not None
        self.process.stdin.write(json.dumps(message, ensure_ascii=False) + "\n")
        self.process.stdin.flush()
        if "id" not in message:
            return None
        try:
            return self._responses.get(timeout=self.timeout)
        except queue.Empty as exc:
            raise TimeoutError(f"Timed out waiting for response to {message.get('method')}") from exc

    def close(self) -> None:
        """Close stdin and terminate the server process safely."""
        if self.process is None:
            return
        process = self.process
        try:
            if process.stdin is not None:
                process.stdin.close()
        except OSError:
            pass
        try:
            process.wait(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        self.process = None

    def restart(self) -> None:
        """Restart the server process using the original command."""
        self.close()
        self.start()

    def stderr_lines(self) -> List[str]:
        """Return stderr lines collected without contaminating stdout protocol data."""
        lines: List[str] = []
        while True:
            try:
                lines.append(self._stderr.get_nowait())
            except queue.Empty:
                return lines

    def _read_stdout(self) -> None:
        assert self.process is not None and self.process.stdout is not None
        for line in self.process.stdout:
            try:
                message = json.loads(line)
                if isinstance(message, dict):
                    self._responses.put(message)
            except json.JSONDecodeError:
                self._stderr.put(f"invalid stdout line: {line.rstrip()}")

    def _read_stderr(self) -> None:
        assert self.process is not None and self.process.stderr is not None
        for line in self.process.stderr:
            self._stderr.put(line.rstrip())


def demo_command() -> List[str]:
    """Return a portable command for launching the demo server."""
    return [sys.executable, "-m", "backend.mcp_core.mcp.stdio_server"]
