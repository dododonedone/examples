// Sign in to dododonedone with OAuth 2.1 and print an access token. No dependencies, Node 18+.
//
// Usage: export DODODONEDONE_TOKEN=$(node get-token.mjs)
//
// The first run registers this script as an OAuth client, opens the browser so you can sign
// in, pick a workspace and approve, and catches the answer on http://127.0.0.1:8976/callback.
// The tokens are saved in .dododonedone-token.json in the current directory (keep it out of
// git). Later runs print the saved access token, or trade the refresh token for a new pair
// when the access token has run out, without the browser.
//
// Set DODODONEDONE_NO_BROWSER=1 to print the sign-in address instead of opening a browser.
import { spawn } from "node:child_process";
import { createHash, randomBytes } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { createServer } from "node:http";

const MCP_URL = process.env.DODODONEDONE_MCP_URL ?? "https://mcp.dododonedone.com/mcp";
const PORT = Number(process.env.DODODONEDONE_CALLBACK_PORT ?? 8976);
const REDIRECT_URI = `http://127.0.0.1:${PORT}/callback`;
const TOKEN_FILE = ".dododonedone-token.json";
const HEADERS = { Accept: "application/json", "User-Agent": "dododonedone-examples-node" };

async function fetchJson(url, options = {}) {
  const response = await fetch(url, { ...options, headers: { ...HEADERS, ...options.headers } });
  if (!response.ok) throw new Error(`${url} answered HTTP ${response.status}: ${await response.text()}`);
  return response.json();
}

// Find the authorization server from the MCP address (RFC 9728, then RFC 8414).
async function discover() {
  const resource = await fetchJson(new URL("/.well-known/oauth-protected-resource", MCP_URL));
  const issuer = resource.authorization_servers[0].replace(/\/$/, "");
  return fetchJson(`${issuer}/.well-known/oauth-authorization-server`);
}

function save(clientId, tokens) {
  const saved = {
    mcp_url: MCP_URL,
    client_id: clientId,
    access_token: tokens.access_token,
    refresh_token: tokens.refresh_token,
    scope: tokens.scope,
    expires_at: Math.floor(Date.now() / 1000) + tokens.expires_in,
  };
  writeFileSync(TOKEN_FILE, JSON.stringify(saved, null, 2), { mode: 0o600 });
  return saved;
}

// Trade the refresh token for a new pair. The old refresh token is used up, so the new one
// must be saved. Returns null when the server refuses it.
async function refresh(server, saved) {
  const response = await fetch(server.token_endpoint, {
    method: "POST",
    headers: HEADERS,
    body: new URLSearchParams({
      grant_type: "refresh_token", refresh_token: saved.refresh_token, client_id: saved.client_id,
    }),
  });
  return response.ok ? save(saved.client_id, await response.json()) : null;
}

function waitForCallback() {
  return new Promise((resolve) => {
    const listener = createServer((request, response) => {
      const url = new URL(request.url, REDIRECT_URI);
      if (url.pathname !== "/callback") {
        response.writeHead(404).end();
        return;
      }
      response.writeHead(200, { "Content-Type": "text/plain; charset=utf-8" });
      response.end("Done. You can close this tab and go back to the terminal.");
      listener.close();
      listener.closeAllConnections();
      resolve(url.searchParams);
    });
    listener.listen(PORT, "127.0.0.1");
  });
}

async function signIn(server) {
  // 1. Register as a public client (RFC 7591). Nothing is granted until you approve.
  const client = await fetchJson(server.registration_endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ client_name: "dododonedone-examples (Node)", redirect_uris: [REDIRECT_URI] }),
  });

  // 2. Send the browser to the authorization endpoint with a PKCE challenge (S256).
  const verifier = randomBytes(48).toString("base64url");
  const challenge = createHash("sha256").update(verifier).digest("base64url");
  const state = randomBytes(16).toString("base64url");
  const url = `${server.authorization_endpoint}?${new URLSearchParams({
    response_type: "code", client_id: client.client_id, redirect_uri: REDIRECT_URI, state,
    code_challenge: challenge, code_challenge_method: "S256",
  })}`;
  console.error(`Sign in and approve in your browser:\n${url}`);
  const callback = waitForCallback();
  if (!process.env.DODODONEDONE_NO_BROWSER) {
    const [command, args] = process.platform === "darwin" ? ["open", [url]]
      : process.platform === "win32" ? ["cmd", ["/c", "start", "", url]] : ["xdg-open", [url]];
    spawn(command, args, { stdio: "ignore", detached: true }).on("error", () => {}).unref();
  }

  // 3. Wait for the redirect back to this machine.
  const answer = await callback;
  if (answer.get("state") !== state) throw new Error("The answer's state doesn't match; start again.");
  if (answer.get("error")) {
    throw new Error(`Not approved: ${answer.get("error")} ${answer.get("error_description") ?? ""}`);
  }

  // 4. Trade the code for an access token and a refresh token.
  const tokens = await fetchJson(server.token_endpoint, {
    method: "POST",
    body: new URLSearchParams({
      grant_type: "authorization_code", code: answer.get("code"), code_verifier: verifier,
      redirect_uri: REDIRECT_URI, client_id: client.client_id,
    }),
  });
  return save(client.client_id, tokens);
}

let saved = existsSync(TOKEN_FILE) ? JSON.parse(readFileSync(TOKEN_FILE, "utf8")) : null;
if (saved?.mcp_url !== MCP_URL) saved = null;
if (!saved || saved.expires_at - 60 < Date.now() / 1000) {
  const server = await discover();
  saved = (saved && (await refresh(server, saved))) ?? (await signIn(server));
}
console.log(saved.access_token);
