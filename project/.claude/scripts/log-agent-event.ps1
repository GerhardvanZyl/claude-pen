# log-agent-event.ps1
# Appends one JSON line per subagent start/stop to .claude/review/runs/_agent-events.jsonl
#
# Claude Code passes hook input as JSON on stdin. This script records timing and
# identity for every subagent regardless of whether the agent remembers to write
# its own log, so the event trail survives an agent that crashes, is stopped, or
# ignores its logging instruction.
#
# Wire it up in settings.json — see settings.example.json two directories up
# (.claude/settings.example.json). Verify with /doctor: this script exits 0 on
# every error so it can never block a subagent, which also means a broken
# invocation is silent. If _agent-events.jsonl is not appearing, the hook is not
# running — check the command path before suspecting this script.

$ErrorActionPreference = 'Stop'

try {
    $raw = [Console]::In.ReadToEnd()
    $payload = $raw | ConvertFrom-Json
} catch {
    exit 0   # never block a subagent because logging failed
}

# Hook cwd is not guaranteed to be the project root. Prefer the harness-provided
# project directory, then the payload's cwd, and only then fall back to wherever
# we happen to be — the last of which is what produces log files in odd places.
$root = $env:CLAUDE_PROJECT_DIR
if (-not $root) { $root = $payload.cwd }
if (-not $root) { $root = (Get-Location).Path }

$dir = Join-Path $root '.claude\review\runs'
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
$logPath = Join-Path $dir '_agent-events.jsonl'

$event = [ordered]@{
    ts         = (Get-Date).ToUniversalTime().ToString('o')
    hook       = $payload.hook_event_name
    agent_type = $payload.agent_type
    agent_id   = $payload.agent_id
    session    = $payload.session_id
    cwd        = $payload.cwd
}

# Stop events may carry an outcome; include whatever is present without assuming.
foreach ($field in 'status','error','duration_ms','total_tokens') {
    if ($payload.PSObject.Properties.Name -contains $field) {
        $event[$field] = $payload.$field
    }
}

$line = ($event | ConvertTo-Json -Compress -Depth 6)

# Parallel subagents append concurrently. Retry briefly rather than losing a line.
for ($i = 0; $i -lt 10; $i++) {
    try {
        $fs = [System.IO.File]::Open($logPath, 'Append', 'Write', 'Read')
        $sw = New-Object System.IO.StreamWriter($fs)
        $sw.WriteLine($line)
        $sw.Flush(); $sw.Close(); $fs.Close()
        break
    } catch {
        Start-Sleep -Milliseconds 50
    }
}

exit 0
