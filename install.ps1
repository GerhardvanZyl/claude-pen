<#
.SYNOPSIS
  Installs everything.
.DESCRIPTION
  Existing user-level agents and skills are backed up before anything is
  overwritten. The backup directory is printed; nothing is deleted.
.EXAMPLE
  .\install.ps1
  .\install.ps1 -Repo C:\path\to\repo
  .\install.ps1 -Repo C:\path\to\repo -WhatIfOnly
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

function Copy-Tree($from, $to, $label, $exclude = @()) {
    if (-not (Test-Path $from)) { return }
    if ($WhatIfOnly) { Write-Host "  would copy $label -> $to"; return }
    New-Item -ItemType Directory -Force -Path $to | Out-Null
    # Resolve the same wildcard this used to hand straight to Copy-Item, so
    # hidden-item and merge semantics are unchanged, then drop the excluded
    # names. Copy-Item's own -Exclude is not usable here: combined with
    # -Recurse it filters at the wrong level and silently drops nested content.
    $items = @(Get-Item (Join-Path $from '*'))
    $skip  = @($exclude)
    if ($skip.Count -gt 0) { $items = @($items | Where-Object { $skip -notcontains $_.Name }) }
    if ($items.Count -gt 0) { Copy-Item -Path $items.FullName -Destination $to -Recurse -Force }
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
$skillsLabel = 'skills (5 loops + solution-architecture + coding-standards + 3 walkthrough)'
Copy-Tree (Join-Path $here 'user\.claude\skills') (Join-Path $claude 'skills') $skillsLabel
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

    # standards.md is user-editable and lives inside the tree Copy-Tree
    # overwrites wholesale. It is kept out of that copy rather than overwritten
    # and put back afterwards: a run that died between the two -- a locked file,
    # a permission error, Ctrl-C -- would take the one file this contract exists
    # to protect, and reading it into a variable and writing it out again is not
    # byte-preserving anyway. The bundled version is written as .new before
    # anything else lands, so a copy that fails partway through has still
    # honoured the same non-clobber contract CLAUDE.md gets above.
    $standardsDest = Join-Path $dest 'standards.md'
    $standardsExisted = Test-Path $standardsDest
    $standardsSkip = @()
    if ($standardsExisted -and -not $WhatIfOnly) {
        Copy-Item (Join-Path $here 'project\.claude\standards.md') (Join-Path $dest 'standards.new.md') -Force
        $standardsSkip = @('standards.md')
    }

    Copy-Tree (Join-Path $here 'project\.claude') $dest 'project layer' $standardsSkip

    if ($WhatIfOnly) {
        if ($standardsExisted) {
            Write-Host "  would NOT overwrite existing $standardsDest -- would write standards.new.md beside it"
        } else {
            Write-Host "  would write $standardsDest"
        }
    } elseif ($standardsExisted) {
        Write-Host "  ! $standardsDest already exists." -ForegroundColor Yellow
        Write-Host "    Wrote standards.new.md beside it -- MERGE MANUALLY, do not overwrite." -ForegroundColor Yellow
    } else {
        Write-Host "  standards.md installed"
    }

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
if ($skills -lt 10) { Write-Host "  ! expected at least 10 skill folders" -ForegroundColor Yellow }
if ($Repo) {
    $ps = (Get-ChildItem (Join-Path $Repo '.claude') -Recurse -File).Count
    Write-Host "  $ps files in $Repo\.claude"
}
if ($didBackup) { Write-Host "  previous agents/skills preserved in $backup" }

Write-Host "`n=== Do these by hand ===" -ForegroundColor Cyan
Write-Host "  * Edit $claude\skills\coding-standards\SKILL.md -- replace its rule sections with"
Write-Host "    your real cross-project rules. Leave its precedence section as shipped."
if ($Repo) {
    Write-Host "  1. Put repository-specific rules in .claude\standards.md, which overrides the"
    Write-Host "     baseline -- optional, leave it alone if there is nothing to override."
    Write-Host "  2. Fill in ARCHITECTURE.template.md, rename to ARCHITECTURE.md at the repo root."
    Write-Host "  3. Fill in the Configuration table in .claude\skills\implement-sprint\SKILL.md"
    Write-Host "     -- tracker, access route, coordinates, code host, base branch. backlog-refinement"
    Write-Host "     reads the same table, and needs its access route to have write access."
}
Write-Host "  * Merge .claude\settings.example.json into .claude\settings.json for hook logging,"
Write-Host "    then run /doctor -- the hook fails silently if its path is wrong."
Write-Host "`nRestart Claude Code once, then run /doctor.`n"
