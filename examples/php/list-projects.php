<?php
// List the projects in the workspace. Reads only.
// Usage: DODODONEDONE_TOKEN=... php list-projects.php
require __DIR__ . '/dododonedone.php';

$result = dododonedone_call_tool('find_projects');

foreach ($result['projects'] as $project) {
    $note = $project['is_inbox'] ? '  (Loose ends, the inbox)' : '';
    echo str_pad($project['name'], 24), ' ', $project['id'], $note, PHP_EOL;
}
