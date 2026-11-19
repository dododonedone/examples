#!/usr/bin/env bash
# Add a task with a due date in plain words.
#
# WRITES TO YOUR ACCOUNT: this adds a task to the workspace the token is for.
#
# Usage: DODODONEDONE_TOKEN=... ./create-task.sh
set -euo pipefail
URL="${DODODONEDONE_MCP_URL:-https://mcp.dododonedone.com/mcp}"

curl -sS --fail-with-body "$URL" \
  -H "Authorization: Bearer $DODODONEDONE_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call",
       "params": {"name": "add_tasks", "arguments": {
         "tasks": [{"title": "Water the tomato plants", "due": "tomorrow at 9"}]}}}'
echo
