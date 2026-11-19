"""Sign in to dododonedone with OAuth 2.1 and print an access token. Standard library only.

Usage: export DODODONEDONE_TOKEN=$(python3 get_token.py)

The first run registers this script as an OAuth client, opens the browser so you can sign
in, pick a workspace and approve, and catches the answer on http://127.0.0.1:8976/callback.
The tokens are saved in .dododonedone-token.json in the current directory (keep it out of
git). Later runs print the saved access token, or trade the refresh token for a new pair
when the access token has run out, without the browser.

Set DODODONEDONE_NO_BROWSER=1 to print the sign-in address instead of opening a browser.
"""
import base64
import hashlib
import http.server
import json
import os
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

MCP_URL = os.environ.get("DODODONEDONE_MCP_URL", "https://mcp.dododonedone.com/mcp")
PORT = int(os.environ.get("DODODONEDONE_CALLBACK_PORT", "8976"))
REDIRECT_URI = f"http://127.0.0.1:{PORT}/callback"
TOKEN_FILE = ".dododonedone-token.json"
HEADERS = {"Accept": "application/json", "User-Agent": "dododonedone-examples-python"}


def fetch(url, form=None, body=None):
    """GET a URL, or POST a form or a JSON body, and return the decoded JSON."""
    headers, data = dict(HEADERS), None
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise SystemExit(f"{url} answered HTTP {error.code}: {error.read().decode('utf-8', 'replace')}")


def discover():
    """Find the authorization server from the MCP address (RFC 9728, then RFC 8414)."""
    origin = "{0.scheme}://{0.netloc}".format(urllib.parse.urlsplit(MCP_URL))
    resource = fetch(origin + "/.well-known/oauth-protected-resource")
    issuer = resource["authorization_servers"][0].rstrip("/")
    return fetch(issuer + "/.well-known/oauth-authorization-server")


def save(saved, client_id, tokens):
    saved.clear()
    saved.update({"mcp_url": MCP_URL, "client_id": client_id, "access_token": tokens["access_token"],
                  "refresh_token": tokens["refresh_token"], "scope": tokens.get("scope"),
                  "expires_at": int(time.time()) + int(tokens["expires_in"])})
    with open(os.open(TOKEN_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w") as handle:
        json.dump(saved, handle, indent=2)


def refresh(server, saved):
    """Trade the refresh token for a new pair. The old refresh token is used up, so the
    new one must be saved. Returns False when the server refuses it."""
    form = {"grant_type": "refresh_token", "refresh_token": saved["refresh_token"], "client_id": saved["client_id"]}
    request = urllib.request.Request(server["token_endpoint"], data=urllib.parse.urlencode(form).encode(),
                                     headers=HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            save(saved, saved["client_id"], json.load(response))
            return True
    except urllib.error.HTTPError:
        return False


def sign_in(server, saved):
    # 1. Register as a public client (RFC 7591). Nothing is granted until you approve.
    client_id = fetch(server["registration_endpoint"], body={
        "client_name": "dododonedone-examples (Python)", "redirect_uris": [REDIRECT_URI]})["client_id"]

    # 2. Send the browser to the authorization endpoint with a PKCE challenge (S256).
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    url = server["authorization_endpoint"] + "?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": client_id, "redirect_uri": REDIRECT_URI, "state": state,
        "code_challenge": challenge, "code_challenge_method": "S256"})
    print("Sign in and approve in your browser:\n" + url, file=sys.stderr)
    if not os.environ.get("DODODONEDONE_NO_BROWSER"):
        webbrowser.open(url)

    # 3. Wait for the redirect back to this machine.
    answer = {}

    class Callback(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            parts = urllib.parse.urlsplit(self.path)
            if parts.path != "/callback":
                self.send_error(404)
                return
            answer.update({key: values[0] for key, values in urllib.parse.parse_qs(parts.query).items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Done. You can close this tab and go back to the terminal.")

        def log_message(self, *args):
            pass

    with http.server.HTTPServer(("127.0.0.1", PORT), Callback) as listener:
        while not answer:
            listener.handle_request()
    if answer.get("state") != state:
        raise SystemExit("The answer's state doesn't match; start again.")
    if "error" in answer:
        raise SystemExit(f"Not approved: {answer['error']} {answer.get('error_description', '')}")

    # 4. Trade the code for an access token and a refresh token.
    tokens = fetch(server["token_endpoint"], form={
        "grant_type": "authorization_code", "code": answer["code"], "code_verifier": verifier,
        "redirect_uri": REDIRECT_URI, "client_id": client_id})
    save(saved, client_id, tokens)


def main():
    saved = {}
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as handle:
            saved = json.load(handle)
    if saved.get("mcp_url") != MCP_URL:
        saved = {}
    if not saved or saved["expires_at"] - 60 < time.time():
        server = discover()
        if not (saved and refresh(server, saved)):
            sign_in(server, saved)
    print(saved["access_token"])


if __name__ == "__main__":
    main()
