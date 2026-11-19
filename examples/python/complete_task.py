"""Mark a task done.

WRITES TO YOUR ACCOUNT: this completes the task in the workspace the token is for.

Usage: DODODONEDONE_TOKEN=... python3 complete_task.py <task id>
"""
import sys

from dododonedone import call_tool

if len(sys.argv) < 2:
    sys.exit("Give a task id (list_tasks.py prints them).")

# complete_tasks takes up to 100 ids in one call and reports failures per id. A recurring
# task also needs occurrence_dates (see docs/mcp.md).
result = call_tool("complete_tasks", {"ids": [sys.argv[1]]})

for failure in result.get("failures", []):
    sys.exit(f"Not completed: {failure['error']['code']}: {failure['error']['message']}")

task = result["tasks"][0]
print("Completed:", task["title"])
print("At:       ", task["completed_at"])
