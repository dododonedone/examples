# dododonedone API examples: your tasks from a script or an AI agent

[![license MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![docs](https://img.shields.io/badge/docs-dododonedone.com-1f5eff)](https://dododonedone.com/docs/mcp)

**List, add and complete your dododonedone tasks from your own code, with due dates written in plain words such as "tomorrow at 9".**

These are runnable examples for [dododonedone](https://dododonedone.com), a to-do list app with its own MCP server, in curl, Python, JavaScript and PHP. The server answers plain HTTP, so you don't need an MCP library: one tool call is one POST with a JSON body and an OAuth access token. The examples have no dependencies, so you can copy one file and run it.

```bash
curl "https://mcp.dododonedone.com/mcp" \
  -H "Authorization: Bearer $DODODONEDONE_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call",
       "params": {"name": "add_tasks", "arguments": {
         "tasks": [{"title": "Water the tomato plants", "due": "tomorrow at 9"}]}}}'
```

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "isError": false,
    "structuredContent": {
      "tasks": [
        {
          "id": "01a1f351-fec5-722f-aa0b-7c314829b7a7",
          "title": "Water the tomato plants",
          "due_date": "2026-11-20",
          "due_time": "09:00",
          "priority": 4,
          "project_id": "678a6202-51f4-50ef-817e-9f8f947a2f73",
          "completed_at": null
        }
      ]
    }
  }
}
```

The answer is shortened here. The full one has every field of the task, and the same JSON once more as text in `result.content`. The server reads "tomorrow at 9" in your time zone, so the date is the day after you run it.

## Get started

1. Create an account at [app.dododonedone.com/signup](https://app.dododonedone.com/signup). Every workspace starts with a 14-day trial of the whole product, and the MCP server is part of it.
2. Get an access token. The script opens your browser, where you sign in, pick the workspace and approve:

   ```bash
   export DODODONEDONE_TOKEN=$(python3 examples/python/get_token.py)
   # or
   export DODODONEDONE_TOKEN=$(node examples/javascript/get-token.mjs)
   ```

3. Run an example:

   ```bash
   python3 examples/python/list_tasks.py
   node examples/javascript/list-tasks.mjs
   php examples/php/list-tasks.php
   ./examples/curl/list-tasks.sh
   ```

The access token works for an hour. Run the same `get_token` command again and it hands you a fresh one without the browser: the script keeps a refresh token in `.dododonedone-token.json` in the folder you run it from. Keep that file out of git (the `.gitignore` here already does).

## The examples

| What you want | Tool | Changes your tasks | curl | Python | JavaScript | PHP |
|---|---|---|---|---|---|---|
| List your open tasks | `find_tasks` | No | [list-tasks.sh](examples/curl/list-tasks.sh) | [list_tasks.py](examples/python/list_tasks.py) | [list-tasks.mjs](examples/javascript/list-tasks.mjs) | [list-tasks.php](examples/php/list-tasks.php) |
| Add a task due "tomorrow at 9" | `add_tasks` | **Yes** | [create-task.sh](examples/curl/create-task.sh) | [create_task.py](examples/python/create_task.py) | [create-task.mjs](examples/javascript/create-task.mjs) | [create-task.php](examples/php/create-task.php) |
| Mark a task done | `complete_tasks` | **Yes** | [complete-task.sh](examples/curl/complete-task.sh) | [complete_task.py](examples/python/complete_task.py) | [complete-task.mjs](examples/javascript/complete-task.mjs) | [complete-task.php](examples/php/complete-task.php) |
| List your projects | `find_projects` | No | [list-projects.sh](examples/curl/list-projects.sh) | [list_projects.py](examples/python/list_projects.py) | [list-projects.mjs](examples/javascript/list-projects.mjs) | [list-projects.php](examples/php/list-projects.php) |
| Sign in and get a token (OAuth 2.1 with PKCE) | | No | | [get_token.py](examples/python/get_token.py) | [get-token.mjs](examples/javascript/get-token.mjs) | |

**The two examples marked "Yes" write to your account**: they add or complete a real task in the workspace you approved. The others only read.

Each language has a small client file (`dododonedone.py`, `dododonedone.mjs`, `dododonedone.php`) of 50 to 75 lines. It sends the token, and raises an error with the server's code when a call fails. The curl scripts print the raw JSON answer.

This is how the examples look when they run:

```
$ python3 examples/python/create_task.py "Book the dentist" "next friday"
Added: Book the dentist
Due:   2026-11-27
Id:    01a1f351-f727-7267-91d1-121088956f10

$ python3 examples/python/list_tasks.py
2026-11-20 09:00  Water the tomato plants  [01a1f351-f6ee-76af-8596-f49d13bfe443]
2026-11-27        Book the dentist  [01a1f351-f727-7267-91d1-121088956f10]

$ python3 examples/python/complete_task.py 01a1f351-f727-7267-91d1-121088956f10
Completed: Book the dentist
At:        2026-11-19T10:19:57.781559Z
```

### Environment variables

| Variable | What | Default |
|---|---|---|
| `DODODONEDONE_TOKEN` | The OAuth access token | none |
| `DODODONEDONE_MCP_URL` | The server address | `https://mcp.dododonedone.com/mcp` |
| `DODODONEDONE_CALLBACK_PORT` | The local port `get_token` listens on for the sign-in answer | `8976` |
| `DODODONEDONE_NO_BROWSER` | Set to `1` and `get_token` prints the sign-in address instead of opening a browser | not set |

## What the server gives you

The server has 32 tools. [docs/mcp.md](docs/mcp.md) lists them all.

- **Tasks**: find, add, update, complete, reopen, reschedule, move, and restore deleted ones.
- **Dates in plain words**: every date argument takes ISO 8601 or words in English or Danish, such as `tomorrow at 9`, `next friday`, `every monday at 8` or `i morgen kl. 9`. A repeat phrase makes the task recurring.
- **Projects, sections, labels and comments**: find and add them.
- **Filters**: run a query in the filter language, such as `today | overdue` or `#Work & p1`, or save it as a named filter.
- **Reminders, the activity log and completed tasks.**
- **Batches**: `add_tasks` takes up to 50 tasks in one call and `complete_tasks` up to 100 ids. One failing item never undoes the others; the answer lists the failures per item.

A change you make shows up on your own devices right away, because the server runs the same operations as the apps.

## Access and limits

| | |
|---|---|
| Address | `https://mcp.dododonedone.com/mcp` (streamable HTTP, stateless, JSON answers) |
| Sign-in | OAuth 2.1 with PKCE (S256). Clients register themselves at `/oauth/register`, so there is no key to copy and nothing to set up first |
| One connection | One user in one workspace, picked on the approval screen |
| Access token | Works for 1 hour |
| Refresh token | Works for 90 days and can be used once: each refresh gives a new pair |
| Default scopes | `tasks:read`, `tasks:write`, `workspace:read`. Ask for `workspace:write` to add and change projects and sections |
| Rate limit | 120 calls a minute per connection and 600 a minute per IP address. Over the limit you get `429` with a `Retry-After` header |

On the approval screen you can choose **Read only**, and the connection can then read but not change anything. Every connection is listed in the app under Settings, Connected apps, where you can revoke it.

A missing or expired token answers `401`. A problem inside a tool comes back as a normal answer with `isError: true` and a code, such as `invalid_arguments`, `insufficient_scope`, `not_found` or `SUBSCRIPTION_INACTIVE`.

## Plans and prices

| | Personal | Team |
|---|---|---|
| For | One person | Teams that share projects |
| Billed yearly | $5 a month | $8 per seat a month |
| Billed monthly | $7 a month | $10 per seat a month |

You can also pay in euros (the same numbers) or Danish kroner (39 or 49 kr. for Personal, 59 or 75 kr. per seat for Team). Prices exclude VAT. There is no free plan: every workspace starts with a 14-day trial with every feature, and you don't need a card to start. The MCP server is part of both plans and of the trial.

When a trial or subscription ends, the workspace becomes read-only: the read tools keep working, and the tools that write answer `SUBSCRIPTION_INACTIVE` until you choose a plan. [See the prices](https://dododonedone.com/pricing).

## Connect an AI client

Claude, Claude Code, Cursor, VS Code and other MCP clients connect to the same address and sign in for you. See [the setup](docs/mcp.md).

## What about the REST API?

There is a REST API at `https://api.dododonedone.com` with an [interactive reference](https://api.dododonedone.com/docs). It is what the web app talks to and it uses the app's own session, so there are no personal API keys for it. For scripts and tools outside the app, the MCP server is the supported way in, and that is what these examples use.

## Documentation

- [Connect your AI over MCP](https://dododonedone.com/docs/mcp): clients, tools, permissions and troubleshooting
- [Server card](https://mcp.dododonedone.com/.well-known/mcp.json): the address, scopes and tool list as JSON
- [API overview](https://dododonedone.com/docs/api)
- [Dates in plain words](https://dododonedone.com/docs/dates) and [the filter language](https://dododonedone.com/docs/filters)

Questions? Write to support@dododonedone.com or open an issue here.

## License

The examples are under the [MIT license](LICENSE). Use them as you like.
