# Remote MCP deployment guide

This guide deploys the remote MCP server and its anonymized PostgreSQL dataset
on one Linux machine, such as a Google Compute Engine VM.

```text
SQL Anywhere local -> anonymized JSON export -> PostgreSQL Docker -> MCP HTTP Docker
```

The original database and its credentials must never be copied to the remote
machine. The remote database contains only the approved analytical dataset.

## 1. Prepare the project

The server needs `backend/`, `database/`, `scripts/`, `Dockerfile.remote`,
`docker-compose.remote.yml`, `.env.remote`, and
`output/remote_sales_anon.json`. Do not commit the output file.

## 2. Configure `.env.remote`

```bash
cd ~/remote_mcp_redes
cp .env.remote.example .env.remote
nano .env.remote
```

Use the same password in both PostgreSQL settings:

```env
MCP_REMOTE_TOKEN=long-random-token
MCP_AUDIT_LOG=/tmp/mcp_audit.jsonl
POSTGRES_DB=remote_sales
POSTGRES_USER=admin
POSTGRES_PASSWORD=strong-password
REMOTE_DATABASE_URL=postgresql://admin:strong-password@postgres:5432/remote_sales
```

## 3. Start PostgreSQL

```bash
sudo docker compose -f docker-compose.remote.yml up -d postgres
sudo docker compose -f docker-compose.remote.yml ps
```

If the database was initialized with another name and contains no required
data, recreate the volume before the first load:

```bash
sudo docker compose -f docker-compose.remote.yml down -v
sudo docker compose -f docker-compose.remote.yml up -d postgres
```

## 4. Load the anonymized JSON

Build the image so it contains the schema and loader:

```bash
sudo docker compose -f docker-compose.remote.yml build --no-cache mcp-remote
```

From the project root, mount the VM output directory into the container:

```bash
sudo docker compose -f docker-compose.remote.yml run --rm \
  -v "$PWD/output:/app/output:ro" \
  mcp-remote \
  python -m scripts.load_postgres /app/output/remote_sales_anon.json
```

Expected output:

```text
Loaded <number> anonymized rows
```

Verify the data:

```bash
sudo docker compose -f docker-compose.remote.yml exec postgres \
  psql -U admin -d remote_sales \
  -c "SELECT COUNT(*) FROM v_lineas_facturadas_analiticas;"
```

## 5. Configure HTTPS and start the MCP

The container supports native Uvicorn TLS. Place a certificate and private key
in `certs/fullchain.pem` and `certs/privkey.pem`, keep them out of Git, and use
these values in `.env.remote`:

```env
MCP_TLS_REQUIRED=true
MCP_TLS_CERTFILE=/certs/fullchain.pem
MCP_TLS_KEYFILE=/certs/privkey.pem
```

Start the service:

```bash
sudo docker compose -f docker-compose.remote.yml up -d --build mcp-remote
curl -k https://127.0.0.1:8080/health
```

List tools:

```bash
curl -k -X POST https://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

Test a real query:

```bash
curl -k -X POST https://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_sales_summary","arguments":{"start_date":"2025-01-01","end_date":"2025-12-31"}}}'
```

## 6. Connect the local client

In the local `.env`, use the VM public IP:

```env
MCP_TRANSPORT=http
MCP_REMOTE_URL=https://PUBLIC_VM_IP:8080/mcp
MCP_REMOTE_TOKEN=long-random-token
MCP_REQUIRE_TLS=true
```

`MCP_REQUIRE_TLS=true` belongs to the local chatbot configuration and makes
the client reject any non-HTTPS remote URL before sending credentials.

Restart the local API after changing `.env`, then start the frontend. The LLM
runs locally while tool calls go to the remote MCP and PostgreSQL dataset.

## Security checklist

- Only use the anonymized export remotely.
- Keep `.env.remote`, passwords, tokens, and salts out of Git.
- Use a read-only database user for the MCP.
- Allow TCP `8080` only from required client IPs.
- Never expose PostgreSQL port `5432` publicly.
- Use HTTPS and a reverse proxy for production.
