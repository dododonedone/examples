"""List the projects in the workspace. Reads only.

Usage: DODODONEDONE_TOKEN=... python3 list_projects.py
"""
from dododonedone import call_tool

result = call_tool("find_projects")

for project in result["projects"]:
    note = "  (Loose ends, the inbox)" if project["is_inbox"] else ""
    print(f"{project['name']:<24} {project['id']}{note}")
