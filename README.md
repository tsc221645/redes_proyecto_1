# Executive Insights — Local MCP Server

Executive Insights is an academic business chatbot for querying sales data in SAP SQL Anywhere 17. It uses manually implemented JSON-RPC 2.0 and MCP, LiteLLM, a standalone local business MCP server, and a Vue web interface.

## Architecture

```text
Vue 3 UI → FastAPI host → LiteLLM → manual MCP client / stdio → business-mcp-server → ODBC read-only → SQL Anywhere 17
```

The business server is an independent process. It reads newline-delimited JSON-RPC messages from standard input and writes responses to standard output. Logs use standard error and an audit JSONL file.

## Requirements

- Windows with Python 3.12+ and Conda environment `dm1`.
- SQL Anywhere 17 and the 64-bit `SQL Anywhere 17` ODBC driver.
- Node.js 18+.
- An API key for a LiteLLM-supported provider.

## Installation

```powershell
conda activate dm1
python -m pip install -r requirements.txt
cd frontend
npm.cmd install
cd ..
```

## Configuration

Copy `.env.example` to `.env` and set local values:

```env
SQLANYWHERE_HOST=127.0.0.1
SQLANYWHERE_PORT=2638
SQLANYWHERE_SERVER=prodin_v17
SQLANYWHERE_DATABASE=
SQLANYWHERE_USER=readonly_user
SQLANYWHERE_PASSWORD=your_password
SQLANYWHERE_DRIVER=SQL Anywhere 17
SQLANYWHERE_READ_ONLY=true
LLM_MODEL=openai/gpt-4o-mini
OPENAI_API_KEY=your_api_key
MCP_AUDIT_LOG=logs/mcp_audit.jsonl
```

Never commit `.env`, passwords, API keys, the complete database, or generated logs.

## Start SQL Anywhere

```powershell
& "C:\Program Files\SQL Anywhere 17\Bin64\dbsrv17.exe" -n PRODIN -x "tcpip(port=2638)" "C:\path\to\PRODIN_V17.DB"
```

Confirm that port `2638` is listening before starting the chatbot.

## Run the standalone MCP server

```powershell
python -m backend.business.server
```

The process waits for JSON-RPC messages on standard input. The chatbot launches it automatically through the manual MCP stdio client.

## Run the chatbot

Terminal 1:

```powershell
C:\Users\alambre1\anaconda3\envs\dm1\python.exe -m uvicorn backend.api.app:app --reload
```

Terminal 2:

```powershell
cd frontend
npm.cmd run dev
```

Open `http://localhost:5173`. API documentation is available at `http://127.0.0.1:8000/docs`.

## MCP specification

The local server supports `initialize`, `notifications/initialized`, `tools/list`, and `tools/call`. Current business tools include `query_business_metrics`, `get_sales_summary`, `compare_periods`, `analyze_product_performance`, and `get_customer_product_mix`. Arguments are validated and SQL is owned by the repository layer; the LLM never sends SQL.

## Examples

```text
What were the monthly sales during 2025?
Which clients buy the most Car Kool Verde?
What other products does the client who buys the most Insta Wax purchase?
Compare sales between 2024 and 2025.
```

The local interface may show real names. A future remote deployment must use a reduced and anonymized dataset.

## Audit logs

The server writes JSON Lines events to `logs/mcp_audit.jsonl` by default. Events include timestamps, direction, JSON-RPC ID, method, tool, safe parameters, duration, and errors. Passwords, tokens, connection strings, and complete business result sets are excluded.

## Testing

```powershell
python -m pytest -q
```

## Structure

```text
backend/mcp_core/       Manual JSON-RPC, MCP, stdio and audit code
backend/business/       Business MCP server and use cases
backend/data_access/    SQL Anywhere ODBC and repositories
backend/llm/            LiteLLM, orchestration, sessions and visualizations
backend/api/            FastAPI application
frontend/               Vue 3 + Vite interface
tests/                  Unit and integration tests
docs/                   Protocol, data model and tool documentation
```
