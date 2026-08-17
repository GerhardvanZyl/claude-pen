<#
.SYNOPSIS
  Installs everything.
.DESCRIPTION
  Existing user-level agents and skills are backed up before anything is
  overwritten. The backup directory is printed; nothing is deleted.
.EXAMPLE
  .\install.ps1
  .\install.ps1 -Repo C:\src\Gateway
  .\install.ps1 -Repo C:\src\Gateway -WhatIfOnly
#>
param(
    [string]$Repo,
    [switch]$WhatIfOnly
)

$ErrorActionPreference = 'Stop'
$here   = Split-Path -Parent $MyInvocation.MyCommand.Path
$claude = Join-Path $HOME '.claude'
$stamp  = Get-Date -Format 'yyyyMMdd-HHmmss'
$backup = Join-Path $claude "backup-$stamp"

function Backup-Tree($path, $label) {
    if (-not (Test-Path $path)) { return }
    if ((Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue).Count -eq 0) { return }
    if ($WhatIfOnly) { Write-Host "  would back up existing $label -> $backup"; return }
    $dest = Join-Path $backup (Split-Path $path -Leaf)
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Copy-Item (Join-Path $path '*') $dest -Recurse -Force
    $script:didBackup = $true
}

function Copy-Tree($from, $to, $label) {
    if (-not (Test-Path $from)) { return }
    if ($WhatIfOnly) { Write-Host "  would copy $label -> $to"; return }
    New-Item -ItemType Directory -Force -Path $to | Out-Null
    Copy-Item (Join-Path $from '*') $to -Recurse -Force
}

function Add-IgnoreRule($repoPath, $rule, $why) {
    $gi = Join-Path $repoPath '.gitignore'
    if ((Test-Path $gi) -and (Select-String -Path $gi -SimpleMatch $rule -Quiet)) {
        Write-Host "  .gitignore already has $rule"
        return
    }
    if ($WhatIfOnly) { Write-Host "  would append $rule to .gitignore"; return }
    Add-Content -Path $gi -Value "`n# $why`n$rule"
    Write-Host "  appended $rule to .gitignore"
}

Write-Host "`n=== User level -> $claude ===" -ForegroundColor Cyan

# Back up first. These trees are overwritten wholesale, and a user's own
# same-named agent or skill would otherwise vanish without a trace.
Backup-Tree (Join-Path $claude 'agents') 'agents'
Backup-Tree (Join-Path $claude 'skills') 'skills'
if ($didBackup) { Write-Host "  backed up existing agents/skills -> $backup" -ForegroundColor Yellow }

Copy-Tree (Join-Path $here 'user\.claude\agents') (Join-Path $claude 'agents') 'agents (22)'
Copy-Tree (Join-Path $here 'user\.claude\skills') (Join-Path $claude 'skills') 'skills (5 loops + solution-architecture + 3 walkthrough)'
if (-not $WhatIfOnly) {
    $userClaude = Join-Path $here 'user\CLAUDE.md'
    $destClaude = Join-Path $claude 'CLAUDE.md'
    if (Test-Path $destClaude) {
        Copy-Item $userClaude (Join-Path $claude 'CLAUDE.new.md') -Force
        Write-Host "  ! $destClaude already exists." -ForegroundColor Yellow
        Write-Host "    Wrote CLAUDE.new.md beside it -- MERGE MANUALLY, do not overwrite." -ForegroundColor Yellow
    } else {
        Copy-Item $userClaude $destClaude -Force
        Write-Host "  CLAUDE.md installed"
    }
}

if ($Repo) {
    if (-not (Test-Path $Repo)) { throw "No such directory: $Repo" }
    $dest = Join-Path $Repo '.claude'
    Write-Host "`n=== Project level -> $dest ===" -ForegroundColor Cyan
    Copy-Tree (Join-Path $here 'project\.claude') $dest 'project layer'

    if (-not $WhatIfOnly) {
        Copy-Item (Join-Path $here 'project\ARCHITECTURE.template.md') $Repo -Force
    }

    # Run output quotes the source it examined. Ignoring it is not a nicety.
    Add-IgnoreRule $Repo '.claude/review/runs/' 'Review lane logs quote the code they read'
}

if ($WhatIfOnly) { Write-Host "`nDry run only. Re-run without -WhatIfOnly to apply.`n"; exit 0 }

Write-Host "`n=== Verify ===" -ForegroundColor Cyan
$agents = (Get-ChildItem (Join-Path $claude 'agents') -Filter *.md -ErrorAction SilentlyContinue).Count
$skills = (Get-ChildItem (Join-Path $claude 'skills') -Directory -ErrorAction SilentlyContinue).Count
Write-Host "  $agents agent files, $skills skill folders in $claude"
if ($agents -lt 22) { Write-Host "  ! expected at least 22 agents" -ForegroundColor Yellow }
if ($skills -lt 9)  { Write-Host "  ! expected at least 9 skill folders" -ForegroundColor Yellow }
if ($Repo) {
    $ps = (Get-ChildItem (Join-Path $Repo '.claude') -Recurse -File).Count
    Write-Host "  $ps files in $Repo\.claude"
}
if ($didBackup) { Write-Host "  previous agents/skills preserved in $backup" }

Write-Host "`n=== Do these by hand ===" -ForegroundColor Cyan
if ($Repo) {
    Write-Host "  1. Edit .claude\skills\coding-standards\SKILL.md -- it is a scaffold."
    Write-Host "  2. Fill in ARCHITECTURE.template.md, rename to ARCHITECTURE.md at the repo root."
    Write-Host "  3. Set org/project/team in .claude\skills\implement-sprint\SKILL.md (Configuration)."
}
Write-Host "  * Merge .claude\settings.example.json into .claude\settings.json for hook logging,"
Write-Host "    then run /doctor -- the hook fails silently if its path is wrong."
Write-Host "`nRestart Claude Code once, then run /doctor.`n"
