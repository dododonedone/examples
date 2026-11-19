"""List your open tasks, ordered by due date. Reads only.

Usage: DODODONEDONE_TOKEN=... python3 list_tasks.py [words to search for]
"""
import sys

from dododonedone import call_tool

arguments = {"limit": 50}
if len(sys.argv) > 1:
    arguments["search"] = " ".join(sys.argv[1:])

result = call_tool("find_tasks", arguments)

for task in result["tasks"]:
    due = " ".join(filter(None, [task["due_date"], task["due_time"]])) or "no date"
    print(f"{due:<17} {task['title']}  [{task['id']}]")
if not result["tasks"]:
    print("No open tasks.")
if result["next_cursor"]:
    print("There are more: pass cursor", result["next_cursor"], "to find_tasks for the next page.")
