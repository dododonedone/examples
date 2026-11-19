<?php
// Minimal client for the dododonedone MCP server. PHP 8.0+ with the curl extension.
//
// The server is stateless: every tool call is one HTTP POST with a JSON-RPC body and an
// OAuth access token. Get a token with get_token.py or get-token.mjs in the folders next
// to this one.

class DododonedoneToolError extends Exception
{
    public function __construct(public string $errorCode, string $message, public ?int $status = null, public ?string $retryAfter = null)
    {
        parent::__construct("$errorCode: $message");
    }
}

/**
 * Call one tool and return its result as an array.
 *
 * Throws DododonedoneToolError when the call fails: code "unauthorized" or "invalid_token"
 * (HTTP 401) means the access token is missing or has expired, "too_many_requests"
 * (HTTP 429) that you hit a rate limit (retryAfter holds the seconds to wait), and codes
 * such as "insufficient_scope", "invalid_arguments" or "SUBSCRIPTION_INACTIVE" come from
 * the tool.
 */
function dododonedone_call_tool(string $name, array $arguments = [], ?string $token = null): array
{
    $url = getenv('DODODONEDONE_MCP_URL') ?: 'https://mcp.dododonedone.com/mcp';
    $token ??= getenv('DODODONEDONE_TOKEN') ?: '';
    $body = json_encode([
        'jsonrpc' => '2.0',
        'id' => 1,
        'method' => 'tools/call',
        'params' => ['name' => $name, 'arguments' => (object) $arguments],
    ]);

    $retryAfter = null;
    $curl = curl_init($url);
    curl_setopt_array($curl, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => $body,
        CURLOPT_HTTPHEADER => [
            "Authorization: Bearer $token",
            'Content-Type: application/json',
            'Accept: application/json, text/event-stream',
        ],
        CURLOPT_USERAGENT => 'dododonedone-examples-php',
        CURLOPT_TIMEOUT => 30,
        CURLOPT_HEADERFUNCTION => function ($curl, $line) use (&$retryAfter) {
            if (stripos($line, 'retry-after:') === 0) {
                $retryAfter = trim(substr($line, 12));
            }
            return strlen($line);
        },
    ]);
    $text = curl_exec($curl);
    if ($text === false) {
        throw new RuntimeException('Request failed: ' . curl_error($curl));
    }
    $status = curl_getinfo($curl, CURLINFO_RESPONSE_CODE);

    $answer = json_decode($text, true);
    if ($status < 200 || $status >= 300) {
        throw new DododonedoneToolError($answer['error'] ?? "http_$status", $answer['error_description'] ?? $text, $status, $retryAfter);
    }
    if (isset($answer['error'])) { // a JSON-RPC error, such as an unknown tool name
        throw new DododonedoneToolError((string) $answer['error']['code'], $answer['error']['message'] ?? '');
    }
    $data = $answer['result']['structuredContent'] ?? [];
    if (!empty($answer['result']['isError'])) {
        throw new DododonedoneToolError($data['error']['code'] ?? 'error', $data['error']['message'] ?? '');
    }
    return $data;
}
