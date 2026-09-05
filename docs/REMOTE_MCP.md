# Remote MCP and anonymized data

The remote transport exposes the same manual JSON-RPC MCP lifecycle over HTTP:

```text
MCP client --POST /mcp--> remote MCP server --> read-only SQL Anywhere copy
```

Start it with the environment configured for the anonymized database:

```powershell
conda activate dm1
python -m uvicorn backend.business.remote_server:app --host 0.0.0.0 --port 8080
```

## Docker deployment

Copy `.env.remote.example` to `.env.remote`, set the remote token and point the
ODBC settings to the isolated anonymized database. Then run:

```powershell
docker compose -f docker-compose.remote.yml up --build -d
docker compose -f docker-compose.remote.yml ps
```

The endpoint will be available at `http://localhost:8080/mcp`. In a real
deployment place it behind HTTPS and a reverse proxy. The image includes the
generic Unix ODBC libraries, but the PostgreSQL deployment does not require
the proprietary SQL Anywhere ODBC driver.

After creating the anonymized export, load it into PostgreSQL from the host:

```powershell
$env:REMOTE_DATABASE_URL="postgresql://admin:YOUR_PASSWORD@127.0.0.1:5432/executive_insights"
python -m scripts.load_postgres output/remote_sales_anon.json
```

Port `5432` is bound only to localhost for this loading step. It should not be
published publicly. Never point the remote deployment at the production
database.

The endpoint is `POST /mcp` and supports `initialize`,
`notifications/initialized`, `tools/list`, and `tools/call`. Set
`MCP_REMOTE_TOKEN` to require `Authorization: Bearer <token>`.

## Stable anonymization

The utility in `backend/data_access/anonymization.py` hashes each value with a
secret salt and entity type. The same source value therefore receives the same
label across rows, preserving joins and analytical relationships without
exposing the original name.

Example for a JSON export from SQL Anywhere:

```powershell
$env:ANONYMIZATION_SALT = "use-a-secret-value"
python -m scripts.anonymize_json input.json output_anon.json
```

The database-backed export is:

```powershell
$env:ANONYMIZATION_SALT = "use-a-secret-value"
python -m scripts.export_anonymized --start-date 2025-01-01 --end-date 2025-12-31 --output output/remote_sales_anon.json
```

The input must be an export created from the approved analytical read model,
not the full production database. Do not commit the salt, input export, output
data, credentials, or real business records.

This export contains aggregate rows from the approved analytical view. The
remote deployment still requires loading this artifact into the isolated remote
database or dataset used by the HTTP MCP server.
