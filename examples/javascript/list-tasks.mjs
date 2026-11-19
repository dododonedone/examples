// List your open tasks, ordered by due date. Reads only.
// Usage: DODODONEDONE_TOKEN=... node list-tasks.mjs [words to search for]
import { callTool } from "./dododonedone.mjs";

const args = { limit: 50 };
if (process.argv.length > 2) args.search = process.argv.slice(2).join(" ");

const result = await callTool("find_tasks", args);

for (const task of result.tasks) {
  const due = [task.due_date, task.due_time].filter(Boolean).join(" ") || "no date";
  console.log(`${due.padEnd(17)} ${task.title}  [${task.id}]`);
}
if (result.tasks.length === 0) console.log("No open tasks.");
if (result.next_cursor) {
  console.log("There are more: pass cursor", result.next_cursor, "to find_tasks for the next page.");
}
