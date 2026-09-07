# Phase 4: official Filesystem and Git MCP servers

The manual client connects to both official reference servers through the Phase
3 stdio transport. The Filesystem server is launched with `npx` and an explicit
allowed directory. The Git server is launched with `uvx` and an explicit
repository.

Install the required runtimes first:

```powershell
npm --version
uvx --version
```

The integration uses these commands on Windows:

```powershell
cmd /c npx -y @modelcontextprotocol/server-filesystem C:\path\to\demo
uvx mcp-server-git --repository C:\path\to\demo
```

Run the reproducible scenario from Python:

```powershell
python -c "from backend.mcp_core.mcp.official_scenario import run_filesystem_git_scenario; print(run_filesystem_git_scenario('phase4_demo'))"
```

To expose the official tools to the main chatbot instead of only running the
scenario, configure the local `.env`:

```env
MCP_OFFICIAL_SERVERS=filesystem,git
MCP_OFFICIAL_WORKSPACE=phase4_demo
```

`backend.business.mcp_runtime.MCPClientPool` then discovers and routes the
official tools through the same LLM/MCP orchestration path as the business
tools.

The scenario creates the empty Git repository before launching `mcp-server-git`
(the official server requires an existing repository at startup), then discovers
tools, writes `README.md`, stages the file, and creates a commit through MCP. It fails explicitly if the installed
server version publishes different tool names. The directory passed to the
Filesystem server is the security boundary; do not pass the project root or a
directory containing credentials.
