#!/usr/bin/env bash
# List your open tasks, ordered by due date. Reads only.
# Usage: DODODONEDONE_TOKEN=... ./list-tasks.sh
set -euo pipefail
URL="${DODODONEDONE_MCP_URL:-https://mcp.dododonedone.com/mcp}"

curl -sS --fail-with-body "$URL" \
  -H "Authorization: Bearer $DODODONEDONE_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call",
       "params": {"name": "find_tasks", "arguments": {"limit": 50}}}'
echo
