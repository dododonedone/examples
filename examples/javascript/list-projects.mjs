// List the projects in the workspace. Reads only.
// Usage: DODODONEDONE_TOKEN=... node list-projects.mjs
import { callTool } from "./dododonedone.mjs";

const result = await callTool("find_projects");

for (const project of result.projects) {
  const note = project.is_inbox ? "  (Loose ends, the inbox)" : "";
  console.log(`${project.name.padEnd(24)} ${project.id}${note}`);
}
