<?php
// List your open tasks, ordered by due date. Reads only.
// Usage: DODODONEDONE_TOKEN=... php list-tasks.php [words to search for]
require __DIR__ . '/dododonedone.php';

$arguments = ['limit' => 50];
if ($argc > 1) {
    $arguments['search'] = implode(' ', array_slice($argv, 1));
}

$result = dododonedone_call_tool('find_tasks', $arguments);

foreach ($result['tasks'] as $task) {
    $due = trim(($task['due_date'] ?? '') . ' ' . ($task['due_time'] ?? '')) ?: 'no date';
    echo str_pad($due, 17), ' ', $task['title'], '  [', $task['id'], ']', PHP_EOL;
}
if (!$result['tasks']) {
    echo 'No open tasks.', PHP_EOL;
}
if ($result['next_cursor']) {
    echo 'There are more: pass cursor ', $result['next_cursor'], ' to find_tasks for the next page.', PHP_EOL;
}
