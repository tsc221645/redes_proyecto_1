# Local business MCP server specification

## Identity

```json
{
  "name": "business-mcp-server",
  "version": "1.0.0",
  "transport": "stdio",
  "protocol": "JSON-RPC 2.0"
}
```

## Lifecycle example

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"executive-insights","version":"1.0.0"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
```

## Tool invocation example

```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_sales_summary","arguments":{"start_date":"2025-01-01","end_date":"2025-12-31"}}}
```

Responses contain `content` for the model and `structuredContent` for the host,
charts, auditing and other consumers.

## Errors

The server uses standard JSON-RPC errors:

- `-32600`: invalid request.
- `-32601`: method or tool not found.
- `-32602`: invalid parameters.
- `-32603`: internal server error.

## Security boundary

The server uses the SQL Anywhere credentials from environment variables and is
configured for read-only access. SQL text is not an accepted tool parameter.
Only repository-owned, parameterized queries can reach the database.
