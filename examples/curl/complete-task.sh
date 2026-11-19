#!/usr/bin/env bash
# Mark a task done.
#
# WRITES TO YOUR ACCOUNT: this completes the task in the workspace the token is for.
#
# Usage: DODODONEDONE_TOKEN=... ./complete-task.sh <task id>
set -euo pipefail
URL="${DODODONEDONE_MCP_URL:-https://mcp.dododonedone.com/mcp}"
ID="${1:?Give a task id (list-tasks.sh prints them)}"

curl -sS --fail-with-body "$URL" \
  -H "Authorization: Bearer $DODODONEDONE_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d "{\"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"tools/call\",
       \"params\": {\"name\": \"complete_tasks\", \"arguments\": {\"ids\": [\"$ID\"]}}}"
echo
