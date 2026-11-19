"""Minimal client for the dododonedone MCP server. Standard library only, Python 3.8+.

The server is stateless: every tool call is one HTTP POST with a JSON-RPC body and an
OAuth access token. Get a token with get_token.py.
"""
import json
import os
import urllib.error
import urllib.request

MCP_URL = os.environ.get("DODODONEDONE_MCP_URL", "https://mcp.dododonedone.com/mcp")


class ToolError(Exception):
    def __init__(self, code, message, status=None, retry_after=None):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.status = status
        self.retry_after = retry_after


def call_tool(name, arguments=None, token=None):
    """Call one tool and return its result as a dict.

    Raises ToolError when the call fails: code "unauthorized" or "invalid_token" (HTTP 401)
    means the access token is missing or has expired, "too_many_requests" (HTTP 429) that
    you hit a rate limit (retry_after holds the seconds to wait), and codes such as
    "insufficient_scope", "invalid_arguments" or "SUBSCRIPTION_INACTIVE" come from the tool.
    """
    token = token if token is not None else os.environ.get("DODODONEDONE_TOKEN", "")
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}}}
    request = urllib.request.Request(MCP_URL, data=json.dumps(body).encode(), method="POST", headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "User-Agent": "dododonedone-examples-python",
    })
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            answer = json.load(response)
    except urllib.error.HTTPError as error:
        text = error.read().decode("utf-8", "replace")
        try:
            problem = json.loads(text)
        except ValueError:
            problem = {}
        raise ToolError(problem.get("error", f"http_{error.code}"), problem.get("error_description", text),
                        error.code, error.headers.get("Retry-After")) from None
    if "error" in answer:  # a JSON-RPC error, such as an unknown tool name
        raise ToolError(str(answer["error"].get("code")), answer["error"].get("message", ""))
    result = answer["result"]
    data = result.get("structuredContent") or {}
    if result.get("isError"):
        problem = data.get("error") or {}
        raise ToolError(problem.get("code", "error"), problem.get("message", ""))
    return data
