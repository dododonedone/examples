# dododonedone MCP server: let an AI agent work in your to-do list

dododonedone runs a remote MCP server, so an AI agent can find, add, reschedule and complete your tasks on its own, with the same operations the apps use.

- **Endpoint:** `https://mcp.dododonedone.com/mcp` (streamable HTTP)
- **Sign-in:** OAuth 2.1 with PKCE. The client registers itself, sends you to dododonedone to sign in, and you pick the workspace and approve. There is no API key to copy.
- **Server card:** [`https://mcp.dododonedone.com/.well-known/mcp.json`](https://mcp.dododonedone.com/.well-known/mcp.json) has the address, the scopes and the live tool list as JSON.

You need a dododonedone account ([sign up](https://app.dododonedone.com/signup)). The MCP server is part of both plans and of the 14-day trial.

A connection is for one user in one workspace. To use a second workspace, connect once more. Every connection is listed in the app under Settings, Connected apps, where you can revoke it or switch it between read-only and allowed to change things.

## Claude Code

```bash
claude mcp add --transport http dododonedone https://mcp.dododonedone.com/mcp
```

Add `--scope user` to have it in every project. Then run `/mcp` in Claude Code, choose dododonedone and sign in. Approve the workspace in the browser window that opens.

## Claude (web and desktop)

Open Customize, then Connectors. Choose "+ Add", then "Add custom connector", and paste `https://mcp.dododonedone.com/mcp`. Leave the OAuth client id and secret empty. Claude sends you to dododonedone to sign in, pick the workspace and approve.

## Cursor

`~/.cursor/mcp.json` for every project, or `.cursor/mcp.json` in one project:

```json
{
  "mcpServers": {
    "dododonedone": {
      "url": "https://mcp.dododonedone.com/mcp"
    }
  }
}
```

Restart Cursor, find dododonedone under its MCP settings and sign in.

## VS Code

`.vscode/mcp.json`:

```json
{
  "servers": {
    "dododonedone": {
      "type": "http",
      "url": "https://mcp.dododonedone.com/mcp"
    }
  }
}
```

Start the server from the file, and VS Code opens the browser for the sign-in.

## Other clients

Any client that speaks streamable HTTP and the MCP authorization flow works: it finds the authorization server from the first `401`, registers itself and signs in with PKCE. The redirect address a client registers must be `https`, or `http` on a loopback address such as `127.0.0.1`.

## Permissions

| Scope | Lets the agent | Granted by default |
|---|---|---|
| `tasks:read` | Read tasks, comments, labels, filters, reminders, activity and completed tasks | Yes |
| `tasks:write` | Add and change tasks, comments, labels, filters and reminders | Yes |
| `workspace:read` | Read projects and sections | Yes |
| `workspace:write` | Add and change projects and sections | No, the client must ask for it |

On the approval screen you can choose **Read only**. The connection then keeps only the read scopes, and a tool that would change something answers `insufficient_scope`.

## Tools

The server has 32 tools. The names follow Todoist's MCP server where the two overlap.

| Tool | What it does | Scope |
|---|---|---|
| `get_overview` | What is overdue, due today and coming up, and the projects with their open task counts | `tasks:read`, `workspace:read` |
| `user_info` | The connected user and workspace: time zone, today's date, role and granted scopes | any |
| `find_tasks` | Search and list tasks by text, project, section, parent, label, priority or assignee | `tasks:read` |
| `find_tasks_by_date` | Open tasks due in a range of days, such as today or this week | `tasks:read` |
| `add_tasks` | Add tasks, with due dates in plain words | `tasks:write` |
| `update_tasks` | Change title, description, schedule, deadline, priority, duration, labels or assignee | `tasks:write` |
| `complete_tasks` | Mark tasks done | `tasks:write` |
| `uncomplete_tasks` | Reopen completed tasks | `tasks:write` |
| `reschedule_tasks` | Move tasks to another date and time without touching their recurrence | `tasks:write` |
| `move_tasks` | Move tasks to another project, section or parent task | `tasks:write` |
| `find_deleted_tasks` | Deleted tasks that can still be restored, for up to 30 days | `tasks:read` |
| `restore_tasks` | Restore deleted tasks and the content deleted with them | `tasks:write` |
| `find_projects` | List the projects the user can see, Loose ends (the inbox) first | `workspace:read` |
| `add_projects` | Create projects, optionally nested under another | `workspace:write` |
| `update_projects` | Rename, describe, recolour, nest, archive or unarchive projects | `workspace:write` |
| `find_sections` | List the sections of a project, or of every project | `workspace:read` |
| `add_sections` | Add sections to projects | `workspace:write` |
| `find_labels` | List the workspace's shared labels and the user's own | `tasks:read` |
| `add_labels` | Create labels | `tasks:write` |
| `find_comments` | Read the comments on a task or a project | `tasks:read` |
| `add_comments` | Comment on tasks or projects | `tasks:write` |
| `find_filters` | List the user's saved filters | `tasks:read` |
| `add_filters` | Save filter queries as named filters | `tasks:write` |
| `run_filter` | Run a filter query, or a saved filter, against the open tasks | `tasks:read` |
| `find_reminders` | List the user's reminders | `tasks:read` |
| `add_reminders` | Add reminders, a number of minutes before a task is due or at a fixed moment | `tasks:write` |
| `find_activity` | The activity log: who added, changed, completed, moved or deleted what | `tasks:read` |
| `find_completed` | Completed tasks, one entry per completion | `tasks:read` |
| `delete_object` | Delete one task, project, section, comment, label, filter or reminder | `tasks:write`, or `workspace:write` for projects and sections |
| `find_board_posts` | Feature requests and bug reports from the workspace's feedback boards | `tasks:read` |
| `update_board_posts` | Set statuses, approve or hide, merge duplicates and turn posts into tasks | `tasks:write` |
| `add_board_replies` | Answer feedback board posts publicly as the team | `tasks:write` |

The server also has two resources, `ddd://projects` and `ddd://filters`, and two prompts, `daily-review` and `weekly-planning`.

### Good to know

- **Dates.** Every date argument takes ISO 8601 (`2026-10-20`, `2026-10-20T14:30`) or plain words in English or Danish: `tomorrow at 9`, `next friday`, `every monday at 8`, `i morgen kl. 9`. They are read in the user's time zone. A repeat phrase makes the task recurring.
- **Batches.** The tools that take lists run every item on its own and answer with the rows that went through plus a `failures` list (left out when nothing failed) with `index`, `error.code` and `error.message` per failed item. Retry only those. `add_tasks` and `update_tasks` take up to 50 items, `complete_tasks`, `reschedule_tasks` and `move_tasks` up to 100.
- **Ids** are UUIDs. Look them up with the `find_` tools.
- **Recurring tasks.** `complete_tasks` needs `occurrence_dates` for a recurring task: a map from the task id to the `due_date` you saw, so a retry never completes a later occurrence.
- **Errors** come back as tool results with `isError: true`; `structuredContent.error` has a `code` and a `message`. Codes include `invalid_arguments`, `invalid_date`, `insufficient_scope`, `not_found`, `forbidden` and `SUBSCRIPTION_INACTIVE` (the trial or subscription has ended, and the workspace reads but doesn't write until a plan is chosen).
- **Limits.** 120 calls a minute per connection and 600 a minute per IP address. Over the limit the server answers `429` with a `Retry-After` header.

## Call the server from your own code

The server is stateless and answers in JSON, so you can call a tool with one HTTP POST and no MCP library. See the [examples](../README.md#the-examples) in curl, Python, JavaScript and PHP.

To get a token yourself, do what [get_token.py](../examples/python/get_token.py) and [get-token.mjs](../examples/javascript/get-token.mjs) do:

1. `GET https://mcp.dododonedone.com/.well-known/oauth-protected-resource` names the authorization server, and `GET /.well-known/oauth-authorization-server` there lists its endpoints.
2. `POST /oauth/register` with `{"client_name": "...", "redirect_uris": ["http://127.0.0.1:8976/callback"]}` gives you a `client_id`.
3. Send the browser to `/oauth/authorize` with `response_type=code`, `client_id`, `redirect_uri`, `state`, `code_challenge` and `code_challenge_method=S256`. The user signs in, picks a workspace and approves, and the browser comes back to your redirect address with `code` and `state`.
4. `POST /oauth/token` as a form with `grant_type=authorization_code`, `code`, `code_verifier`, `redirect_uri` and `client_id` gives an access token (1 hour) and a refresh token (90 days).
5. When the access token runs out, `POST /oauth/token` with `grant_type=refresh_token`, `refresh_token` and `client_id` gives a new pair. Save the new refresh token: the old one is used up.

## Things to ask

- "What is overdue, and what is due today? Suggest an order."
- "Add a task to book the dentist next friday, and one to water the tomato plants every monday at 8."
- "Move everything I didn't finish today to tomorrow."
