#!/usr/bin/env pwsh
# Verifies the filesystem contract install.ps1 promises -- the PowerShell mirror
# of tests/install-contract.sh, assertion for assertion:
#   - baseline coding-standards skill lands at the user level, not the project level
#   - <repo>/.claude/standards.md is installed once and never clobbered on re-install
#   - an edited standards.md survives a re-install byte-for-byte, with the bundled
#     version offered beside it as standards.new.md
#   - a missing standards.md is restored, with no .new file left behind
#   - an install that fails partway through destroys neither
#   - -WhatIfOnly writes nothing, anywhere
#
# This script runs install.ps1; it does not reimplement the installer's logic.
# $HOME is a ReadOnly, AllScope automatic variable that $env:HOME does not feed
# on Windows, so it is redirected with Set-Variable -Force and install.ps1 is
# invoked in-process (&) to inherit the redirection. Everything the run touches
# lives under one scratch directory removed in the finally block, so the real
# ~/.claude and the real repository are never written to.
#
# No Set-StrictMode on purpose: install.ps1 runs in a child scope of this script
# and reads $didBackup before it is ever assigned, which strict mode would turn
# into a failure of the installer rather than a failure of the contract.
#
# Convention, matching install-contract.sh: no test framework, no dependencies,
# one line of output per assertion, exit non-zero on the first failure.
$ErrorActionPreference = 'Stop'

$RepoRoot         = Split-Path -Parent $PSScriptRoot
$InstallPs1       = Join-Path $RepoRoot 'install.ps1'
$BundledStandards = Join-Path $RepoRoot 'project\.claude\standards.md'

if (-not (Test-Path -LiteralPath $InstallPs1)) {
    [Console]::Error.WriteLine("FAIL: setup -- install.ps1 not found at $InstallPs1")
    exit 1
}

$TmpRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('install-contract-' + [guid]::NewGuid().ToString('N'))
$TmpHome = Join-Path $TmpRoot 'home'
$TmpWork = Join-Path $TmpRoot 'work'
New-Item -ItemType Directory -Force -Path $TmpHome, $TmpWork | Out-Null

Set-Variable -Name HOME -Value $TmpHome -Force
if ($HOME -ne $TmpHome) {
    [Console]::Error.WriteLine(
        "FAIL: setup -- could not redirect HOME to $TmpHome; refusing to run against the real ~/.claude")
    Remove-Item -LiteralPath $TmpRoot -Recurse -Force -ErrorAction SilentlyContinue
    exit 1
}

$script:Assertions      = 0
$script:FailDescription = $null
$script:FailDetail      = $null

function Pass($description) {
    $script:Assertions++
    Write-Host "PASS: $description"
}

# Records the failure and unwinds: the catch below turns it into one FAIL line
# and a non-zero exit, and the finally block still gets to clean up.
function Assert-Fail($description, $detail) {
    $script:FailDescription = $description
    $script:FailDetail      = $detail
    throw 'contract assertion failed'
}

function Assert-Exists($path, $description) {
    if (Test-Path -LiteralPath $path) { Pass $description }
    else { Assert-Fail $description "expected to exist: $path" }
}

function Assert-NotExists($path, $description) {
    if (-not (Test-Path -LiteralPath $path)) { Pass $description }
    else { Assert-Fail $description "expected NOT to exist: $path" }
}

# Compares bytes, not text. A file that survived as a string but was re-encoded
# on the way back -- a dropped BOM, a codepage change, rewritten line endings --
# is a modified file, and the point of the non-clobber contract is that it is
# not modified.
function Assert-FilesIdentical($a, $b, $description) {
    if (-not (Test-Path -LiteralPath $a)) { Assert-Fail $description "missing: $a" }
    if (-not (Test-Path -LiteralPath $b)) { Assert-Fail $description "missing: $b" }
    $x = [System.IO.File]::ReadAllBytes($a)
    $y = [System.IO.File]::ReadAllBytes($b)
    if ($x.Length -ne $y.Length) {
        $detail = "byte length differs: {0} is {1} bytes, {2} is {3} bytes" -f $a, $x.Length, $b, $y.Length
        Assert-Fail $description $detail
    }
    for ($i = 0; $i -lt $x.Length; $i++) {
        if ($x[$i] -ne $y[$i]) {
            $detail = "{0} vs {1} first differ at byte {2}: 0x{3:x2} vs 0x{4:x2}" -f $a, $b, $i, $x[$i], $y[$i]
            Assert-Fail $description $detail
        }
    }
    Pass $description
}

# Deliberately not plain ASCII: a UTF-8 BOM, a non-ASCII character, a CRLF and
# no trailing newline. A restore that round-trips the file through a text decode
# instead of copying its bytes changes at least one of those whatever the host's
# default encoding is, so Assert-FilesIdentical catches a file that was reported
# untouched but was really rewritten.
function Write-Sentinel($path, $tag) {
    $bom  = [byte[]](0xEF, 0xBB, 0xBF)
    $body = [System.Text.Encoding]::UTF8.GetBytes("# $tag`r`nnon-ASCII $([char]0x2014) and no trailing newline")
    [System.IO.File]::WriteAllBytes($path, $bom + $body)
}

# Content digest of a directory tree: relative path plus hash of every file.
# Used to prove -WhatIfOnly left a tree byte-for-byte alone.
function Get-TreeDigest($dir) {
    if (-not (Test-Path -LiteralPath $dir)) { return "MISSING:$dir" }
    $lines = Get-ChildItem -LiteralPath $dir -Recurse -File -Force |
        Sort-Object FullName |
        ForEach-Object {
            $_.FullName.Substring($dir.Length) + '|' + (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
        }
    return ($lines -join "`n")
}

function Invoke-Install {
    param(
        [string]$Label,
        [string]$RepoPath,
        [switch]$DryRun,
        [switch]$ExpectFailure
    )
    $log = Join-Path $TmpWork ('log-' + ($Label -replace '[^A-Za-z0-9]+', '-') + '.txt')
    $global:LASTEXITCODE = 0
    $threw = $false
    try {
        if ($DryRun) { & $InstallPs1 -Repo $RepoPath -WhatIfOnly *>&1 | Out-File -LiteralPath $log -Encoding utf8 }
        else         { & $InstallPs1 -Repo $RepoPath             *>&1 | Out-File -LiteralPath $log -Encoding utf8 }
    } catch {
        $threw = $true
        ($_ | Out-String) | Add-Content -LiteralPath $log
    }
    $failed = $threw -or ($LASTEXITCODE -ne 0)
    if ($ExpectFailure -and -not $failed) {
        Assert-Fail "$Label -- install.ps1 was expected to fail but completed" "see $log"
    }
    if (-not $ExpectFailure -and $failed) {
        Assert-Fail "$Label -- install.ps1 did not complete" "see $log"
    }
}

$exitCode   = 0
$lockHandle = $null
try {
    Write-Host '=== Fresh install into an empty scratch repo ==='
    $scratch = Join-Path $TmpWork 'repo'
    New-Item -ItemType Directory -Force -Path $scratch | Out-Null
    Invoke-Install -Label 'fresh install' -RepoPath $scratch

    Assert-Exists (Join-Path $TmpHome '.claude\skills\coding-standards\SKILL.md') `
        'baseline coding-standards skill lands at user level'
    Assert-Exists (Join-Path $scratch '.claude\standards.md') `
        'per-repo standards.md is installed'
    Assert-NotExists (Join-Path $scratch '.claude\skills\coding-standards') `
        'project-level coding-standards skill does not come back'
    Assert-Exists (Join-Path $scratch '.claude\skills\implement-sprint') `
        'bulk project-layer copy still lands implement-sprint'
    Assert-Exists (Join-Path $scratch '.claude\skills\sprint-planning\SKILL.md') `
        'bulk project-layer copy still lands sprint-planning'
    Assert-NotExists (Join-Path $scratch '.claude\standards.new.md') `
        'no standards.new.md on a fresh install'

    Write-Host ''
    Write-Host '=== Re-install over an edited standards.md ==='
    $sentinelTag = "SENTINEL-install-contract-test-$PID-$([DateTimeOffset]::UtcNow.ToUnixTimeSeconds())"
    Write-Sentinel (Join-Path $scratch '.claude\standards.md') $sentinelTag
    $expectedSentinel = Join-Path $TmpWork 'expected-sentinel.md'
    Copy-Item (Join-Path $scratch '.claude\standards.md') $expectedSentinel -Force

    Invoke-Install -Label 're-install over edited standards.md' -RepoPath $scratch

    Assert-FilesIdentical (Join-Path $scratch '.claude\standards.md') $expectedSentinel `
        'edited standards.md survives re-install byte-identical'
    Assert-Exists (Join-Path $scratch '.claude\standards.new.md') `
        'bundled version offered as standards.new.md'
    Assert-FilesIdentical (Join-Path $scratch '.claude\standards.new.md') $BundledStandards `
        'standards.new.md matches the bundled project/.claude/standards.md'

    Write-Host ''
    Write-Host '=== Re-install with standards.md missing, rest of .claude present ==='
    Remove-Item -LiteralPath (Join-Path $scratch '.claude\standards.md') -Force
    Remove-Item -LiteralPath (Join-Path $scratch '.claude\standards.new.md') -Force

    Invoke-Install -Label 're-install with standards.md missing' -RepoPath $scratch

    Assert-Exists (Join-Path $scratch '.claude\standards.md') `
        'standards.md is restored when missing'
    Assert-FilesIdentical (Join-Path $scratch '.claude\standards.md') $BundledStandards `
        'restored standards.md matches the bundled version'
    Assert-NotExists (Join-Path $scratch '.claude\standards.new.md') `
        'no standards.new.md appears when nothing needed merging'

    Write-Host ''
    Write-Host '=== Dry run writes nothing ==='
    $homeSkillsBefore = Get-TreeDigest (Join-Path $TmpHome '.claude\skills')
    $dryScratch = Join-Path $TmpWork 'dryrun-repo'
    New-Item -ItemType Directory -Force -Path $dryScratch | Out-Null

    Invoke-Install -Label 'dry run' -RepoPath $dryScratch -DryRun

    Assert-NotExists (Join-Path $dryScratch '.claude') `
        'dry run into a fresh scratch dir writes no .claude directory'
    if ($homeSkillsBefore -eq (Get-TreeDigest (Join-Path $TmpHome '.claude\skills'))) {
        Pass 'dry run leaves HOME/.claude/skills unchanged'
    } else {
        Assert-Fail 'dry run leaves HOME/.claude/skills unchanged' 'tree digest changed'
    }

    Write-Host ''
    Write-Host '=== A failure mid-install does not destroy the repository standards.md ==='
    # The project layer is copied over <repo>\.claude wholesale and standards.md
    # lives inside it, so anything that can fail while that copy is in flight can
    # take the one file the non-clobber contract promises to leave alone. The
    # injection is the security lane's own reproduction: an exclusive handle on a
    # file the copy has to overwrite makes Copy-Item throw part way through, and
    # $ErrorActionPreference = 'Stop' turns that into an aborted install. No test
    # hook inside the installer is needed to provoke it.
    $fault = Join-Path $TmpWork 'fault-repo'
    New-Item -ItemType Directory -Force -Path $fault | Out-Null
    Invoke-Install -Label 'fresh install into the fault-injection repo' -RepoPath $fault

    Write-Sentinel (Join-Path $fault '.claude\standards.md') "$sentinelTag-fault"
    $expectedFault = Join-Path $TmpWork 'expected-fault.md'
    Copy-Item (Join-Path $fault '.claude\standards.md') $expectedFault -Force

    $victim = Join-Path $fault '.claude\skills\implement-sprint\SKILL.md'
    $lockHandle = [System.IO.File]::Open(
        $victim,
        [System.IO.FileMode]::Open,
        [System.IO.FileAccess]::ReadWrite,
        [System.IO.FileShare]::None)

    Invoke-Install -Label 're-install that fails partway through' -RepoPath $fault -ExpectFailure

    $lockHandle.Dispose()
    $lockHandle = $null

    Assert-FilesIdentical (Join-Path $fault '.claude\standards.md') $expectedFault `
        'an install that fails partway through leaves the edited standards.md intact'
    Assert-Exists (Join-Path $fault '.claude\standards.new.md') `
        'an install that fails partway through still honours the standards.new.md contract'

    Write-Host ''
    Write-Host "All $script:Assertions assertions passed."
} catch {
    $exitCode = 1
    if ($script:FailDescription) {
        [Console]::Error.WriteLine("FAIL: $script:FailDescription")
        if ($script:FailDetail) { [Console]::Error.WriteLine("  $script:FailDetail") }
    } else {
        [Console]::Error.WriteLine(
            "FAIL: unexpected error at line $($_.InvocationInfo.ScriptLineNumber) -- $($_.Exception.Message)")
    }
} finally {
    if ($lockHandle) { $lockHandle.Dispose() }
    Remove-Item -LiteralPath $TmpRoot -Recurse -Force -ErrorAction SilentlyContinue
}

exit $exitCode
