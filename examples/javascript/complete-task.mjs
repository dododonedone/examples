// Mark a task done.
//
// WRITES TO YOUR ACCOUNT: this completes the task in the workspace the token is for.
//
// Usage: DODODONEDONE_TOKEN=... node complete-task.mjs <task id>
import { callTool } from "./dododonedone.mjs";

const id = process.argv[2];
if (!id) {
  console.error("Give a task id (list-tasks.mjs prints them).");
  process.exit(1);
}

// complete_tasks takes up to 100 ids in one call and reports failures per id. A recurring
// task also needs occurrence_dates (see docs/mcp.md).
const result = await callTool("complete_tasks", { ids: [id] });

for (const failure of result.failures ?? []) {
  console.error(`Not completed: ${failure.error.code}: ${failure.error.message}`);
  process.exit(1);
}

const task = result.tasks[0];
console.log("Completed:", task.title);
console.log("At:       ", task.completed_at);
