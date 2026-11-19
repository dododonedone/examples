<?php
// Mark a task done.
//
// WRITES TO YOUR ACCOUNT: this completes the task in the workspace the token is for.
//
// Usage: DODODONEDONE_TOKEN=... php complete-task.php <task id>
require __DIR__ . '/dododonedone.php';

if ($argc < 2) {
    fwrite(STDERR, 'Give a task id (list-tasks.php prints them).' . PHP_EOL);
    exit(1);
}

// complete_tasks takes up to 100 ids in one call and reports failures per id. A recurring
// task also needs occurrence_dates (see docs/mcp.md).
$result = dododonedone_call_tool('complete_tasks', ['ids' => [$argv[1]]]);

foreach ($result['failures'] ?? [] as $failure) {
    fwrite(STDERR, "Not completed: {$failure['error']['code']}: {$failure['error']['message']}" . PHP_EOL);
    exit(1);
}

$task = $result['tasks'][0];
echo 'Completed: ', $task['title'], PHP_EOL;
echo 'At:        ', $task['completed_at'], PHP_EOL;
