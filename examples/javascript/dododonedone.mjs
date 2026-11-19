// Minimal client for the dododonedone MCP server. No dependencies, Node 18+ (built-in fetch).
//
// The server is stateless: every tool call is one HTTP POST with a JSON-RPC body and an
// OAuth access token. Get a token with get-token.mjs.
const MCP_URL = process.env.DODODONEDONE_MCP_URL ?? "https://mcp.dododonedone.com/mcp";

export class ToolError extends Error {
  constructor(code, message, status, retryAfter) {
    super(`${code}: ${message}`);
    this.code = code;
    this.status = status;
    this.retryAfter = retryAfter;
  }
}

// Call one tool and return its result as an object. Throws ToolError when the call fails:
// code "unauthorized" or "invalid_token" (HTTP 401) means the access token is missing or
// has expired, "too_many_requests" (HTTP 429) that you hit a rate limit (retryAfter holds
// the seconds to wait), and codes such as "insufficient_scope", "invalid_arguments" or
// "SUBSCRIPTION_INACTIVE" come from the tool.
export async function callTool(name, args = {}, token = process.env.DODODONEDONE_TOKEN ?? "") {
  const response = await fetch(MCP_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      Accept: "application/json, text/event-stream",
      "User-Agent": "dododonedone-examples-node",
    },
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "tools/call", params: { name, arguments: args } }),
  });
  if (!response.ok) {
    const text = await response.text();
    let problem = {};
    try {
      problem = JSON.parse(text);
    } catch {}
    throw new ToolError(problem.error ?? `http_${response.status}`, problem.error_description ?? text,
      response.status, response.headers.get("retry-after"));
  }
  const answer = await response.json();
  if (answer.error) throw new ToolError(String(answer.error.code), answer.error.message); // such as an unknown tool name
  const data = answer.result.structuredContent ?? {};
  if (answer.result.isError) throw new ToolError(data.error?.code ?? "error", data.error?.message ?? "");
  return data;
}
