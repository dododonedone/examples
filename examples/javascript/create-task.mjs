// Add a task with a due date in plain words.
//
// WRITES TO YOUR ACCOUNT: this adds a task to the workspace the token is for.
//
// Usage: DODODONEDONE_TOKEN=... node create-task.mjs "Water the tomato plants" "tomorrow at 9"
import { callTool } from "./dododonedone.mjs";

const title = process.argv[2] ?? "Water the tomato plants";
const due = process.argv[3] ?? "tomorrow at 9";

// add_tasks takes up to 50 tasks in one call. A task without project_id lands in Loose ends.
const result = await callTool("add_tasks", { tasks: [{ title, due }] });

for (const failure of result.failures ?? []) {
  console.error(`Not added: ${failure.error.code}: ${failure.error.message}`);
  process.exit(1);
}

const task = result.tasks[0];
console.log("Added:", task.title);
console.log("Due:  ", task.due_date, task.due_time ?? "");
console.log("Id:   ", task.id);
