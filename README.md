# Executive Insights

Executive Insights is an academic business analytics chatbot. It combines a
Vue interface, a FastAPI host, LiteLLM, and a manually implemented JSON-RPC 2.0
and Model Context Protocol (MCP) layer. The application answers controlled
business questions using sales data without allowing the language model to
submit arbitrary SQL.

## Features

- Natural-language sales analysis in Spanish or English.
- Local MCP server over newline-delimited stdio.
- Remote MCP server over HTTP.
- Optional integration of the official Filesystem and Git MCP servers into the
  same chatbot tool catalog.
- LiteLLM provider abstraction for switching LLM providers.
- SQL Anywhere 17 access for local development.
- PostgreSQL dataset for remote deployment.
- Stable anonymization of clients, products, brands, lines, countries, and invoices.
- Business tools for summaries, period comparisons, product performance, metrics, and customer product mix.
- JSON-RPC audit logging with secrets and full result sets excluded.
- Vue chat interface with Markdown responses and optional charts.
- Automated tests for JSON-RPC, MCP, data access, orchestration, API, sessions, and anonymization.

## Architecture

```text
Local:  Vue -> FastAPI -> LiteLLM -> MCP stdio -> SQL Anywhere
Remote: Client/API -> HTTP JSON-RPC -> MCP Docker -> PostgreSQL anonymized dataset
```

## Requirements

- Python 3.12+ (Conda environment is recommended).
- Node.js 18+.
- For local mode: SQL Anywhere 17 and its 64-bit ODBC driver.
- An API key for the selected LiteLLM provider.
- For remote mode: Docker and Docker Compose.

## Local installation

```powershell
conda create -n dm1 python=3.12
conda activate dm1
python -m pip install -r requirements.txt
cd frontend
npm.cmd install
cd ..
```

Copy `.env.example` to `.env` and set the SQL Anywhere and LLM values. Never
commit `.env`, database files, credentials, API keys, or generated logs.

## Local usage

Start SQL Anywhere separately, then run the API:

```powershell
conda activate dm1
python -m uvicorn backend.api.app:app --reload
```

In another terminal:

```powershell
cd frontend
npm.cmd run dev
```

Open `http://localhost:5173`. The API documentation is available at
`http://127.0.0.1:8000/docs`. The API starts the local business MCP process
automatically. `levantar_proyecto.bat` starts the API and frontend when the
database is already running.

## Remote usage

Follow [docs/REMOTE_MCP.md](docs/REMOTE_MCP.md). It describes anonymized export,
PostgreSQL loading, Docker deployment, Compute Engine setup, and MCP tests.

For HTTPS deployment, mount certificates under `certs/` and configure
`MCP_TLS_CERTFILE`, `MCP_TLS_KEYFILE`, and `MCP_TLS_REQUIRED=true` in
`.env.remote`. The remote client can enforce HTTPS with `MCP_REQUIRE_TLS=true`.
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and
[docs/NETWORK.md](docs/NETWORK.md) for the complete component and network
diagrams.

## Official Filesystem and Git servers

The chatbot can include tools discovered from the official servers in its same
LLM/MCP tool catalog. Install Node.js/npm and `uvx`, then set:

```env
MCP_OFFICIAL_SERVERS=filesystem,git
MCP_OFFICIAL_WORKSPACE=phase4_demo
```

The workspace is the Filesystem security boundary. Git initialization is done
once locally because the official Git server requires an existing repository;
file writes, staging, and commits are then performed through MCP tools. See
`docs/PHASE_4.md` for the reproducible scenario and runtime requirements.

If either external runtime is unavailable, the API reports the startup error;
install and verify them before enabling the corresponding server.

## MCP protocol and tools

The servers implement `initialize`, `notifications/initialized`, `tools/list`,
and `tools/call`. Current tools are `query_business_metrics`,
`get_sales_summary`, `compare_periods`, `analyze_product_performance`, and
`get_customer_product_mix`. Tool schemas validate arguments; SQL remains in
the repository and the LLM never receives a SQL execution tool.

## Testing and code quality

```powershell
conda activate dm1
python -m pytest -q
python -m compileall -q backend scripts
```

The code uses typed Python modules, small repository/use-case boundaries,
parameterized queries, explicit error handling, and docstrings for public
components. Generated files are excluded through `.gitignore`.

## Audit logs

Audit events are written to `logs/mcp_audit.jsonl` by default. They contain
timestamps, direction, method, tool, safe parameters, duration, and errors.
Passwords, tokens, connection strings, and complete business result sets are
not recorded.

## Troubleshooting

- `Missing API key`: set the provider-specific key named in `.env`.
- `stdio server is not running`: verify SQL Anywhere credentials and that
  `python -m backend.business.server` starts without errors.
- `UnicodeDecodeError` in `stdio_client.py`: restart the API after pulling the
  current version; stdio JSON-RPC now escapes non-ASCII characters to remain
  compatible with Windows code pages.
- `npx`/`uvx` errors: install Node.js/npm and `uv`, then verify `npm --version`
  and `uvx --version`.
- `Remote MCP authentication is not configured`: set a non-empty
  `MCP_REMOTE_TOKEN` in `.env.remote`.
- TLS startup failure: verify both certificate files exist at the paths in
  `MCP_TLS_CERTFILE` and `MCP_TLS_KEYFILE`.
- Tests cannot import modules: run `python -m pip install -r requirements.txt`
  inside the active environment.

## Repository layout

```text
backend/mcp_core/       Manual JSON-RPC, MCP, transports, and audit logging
backend/business/       Business tools and local/remote MCP entry points
backend/data_access/    SQL Anywhere and PostgreSQL repositories
backend/llm/            LiteLLM provider, orchestration, sessions, charts
backend/api/            FastAPI application
database/               Remote PostgreSQL schema
scripts/                Anonymization, export, and PostgreSQL loading tools
frontend/               Vue 3 and Vite interface
tests/                  Automated tests
docs/                   Local and remote operation documentation
```
