<?php
// Add a task with a due date in plain words.
//
// WRITES TO YOUR ACCOUNT: this adds a task to the workspace the token is for.
//
// Usage: DODODONEDONE_TOKEN=... php create-task.php "Water the tomato plants" "tomorrow at 9"
require __DIR__ . '/dododonedone.php';

$title = $argv[1] ?? 'Water the tomato plants';
$due = $argv[2] ?? 'tomorrow at 9';

// add_tasks takes up to 50 tasks in one call. A task without project_id lands in Loose ends.
$result = dododonedone_call_tool('add_tasks', ['tasks' => [['title' => $title, 'due' => $due]]]);

foreach ($result['failures'] ?? [] as $failure) {
    fwrite(STDERR, "Not added: {$failure['error']['code']}: {$failure['error']['message']}" . PHP_EOL);
    exit(1);
}

$task = $result['tasks'][0];
echo 'Added: ', $task['title'], PHP_EOL;
echo 'Due:   ', $task['due_date'], ' ', $task['due_time'] ?? '', PHP_EOL;
echo 'Id:    ', $task['id'], PHP_EOL;
