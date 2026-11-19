"""Add a task with a due date in plain words.

WRITES TO YOUR ACCOUNT: this adds a task to the workspace the token is for.

Usage: DODODONEDONE_TOKEN=... python3 create_task.py "Water the tomato plants" "tomorrow at 9"
"""
import sys

from dododonedone import call_tool

title = sys.argv[1] if len(sys.argv) > 1 else "Water the tomato plants"
due = sys.argv[2] if len(sys.argv) > 2 else "tomorrow at 9"

# add_tasks takes up to 50 tasks in one call. A task without project_id lands in Loose ends.
result = call_tool("add_tasks", {"tasks": [{"title": title, "due": due}]})

for failure in result.get("failures", []):
    sys.exit(f"Not added: {failure['error']['code']}: {failure['error']['message']}")

task = result["tasks"][0]
print("Added:", task["title"])
print("Due:  ", task["due_date"], task["due_time"] or "")
print("Id:   ", task["id"])
