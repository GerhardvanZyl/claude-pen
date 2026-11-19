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
#   - the vendored dev-loop-inspector mod is complete, its two manifests agree
#     on the plugin name, and the installer prints the enablement commands
#     while writing nothing at all for it
#   - the printed enablement commands name the shells their quoting is for, and
#     are safe to paste from a bundle directory whose name carries shell
#     metacharacters -- pasted into PowerShell and into cmd.exe
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
$script:LastInstallLog  = $null
$ModHeader              = '=== Mod: dev-loop-inspector ==='

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

# Case-sensitive on purpose: every value this compares is a plugin or
# marketplace name the CLI matches exactly, so a difference in case is a
# difference.
function Assert-Equal($actual, $expected, $description) {
    if ([string]$actual -ceq [string]$expected) { Pass $description }
    else { Assert-Fail $description "expected [$expected], got [$actual]" }
}

# Literal substring checks against a captured install log. .Contains rather
# than -match: every needle here is a command line full of slashes, dots and
# dashes, and none of it is meant as a regex.
function Assert-LogContains($log, $needle, $description) {
    $text = Get-Content -Raw -LiteralPath $log
    if ($text -and $text.Contains($needle)) { Pass $description }
    else { Assert-Fail $description "not in ${log}: $needle" }
}

function Assert-LogLacks($log, $needle, $description) {
    $text = Get-Content -Raw -LiteralPath $log
    if ($text -and $text.Contains($needle)) { Assert-Fail $description "found in ${log}: $needle" }
    else { Pass $description }
}

# Everything the installer prints for the mod, from its section header up to the
# next section. The idempotence assertion compares two of these rather than two
# whole logs because the surrounding output names a backup directory stamped to
# the second, which differs between two runs by construction.
function Get-ModSection($log) {
    $out       = New-Object System.Collections.Generic.List[string]
    $inSection = $false
    foreach ($line in [System.IO.File]::ReadAllLines($log)) {
        if ($inSection -and $line.StartsWith('=== ')) { break }
        if ($line -eq $ModHeader) { $inSection = $true }
        if ($inSection) { $out.Add($line) }
    }
    return ($out -join "`n")
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
    $script:LastInstallLog = $log
    $global:LASTEXITCODE = 0
    $threw = $false
    # -Width because Out-File truncates each line at the host's width otherwise,
    # and the longest line the installer prints is a quoted absolute path -- for
    # a bundle unzipped a few directories deep that is past any default, and a
    # truncated line would fail a literal assertion for the wrong reason.
    try {
        if ($DryRun) { & $InstallPs1 -Repo $RepoPath -WhatIfOnly *>&1 |
                            Out-File -LiteralPath $log -Encoding utf8 -Width 4096 }
        else         { & $InstallPs1 -Repo $RepoPath             *>&1 |
                            Out-File -LiteralPath $log -Encoding utf8 -Width 4096 }
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
    # Baseline for the plugin-registry assertion in the mod section, taken here
    # and not beside the install it guards: $TmpHome is still pristine, so a
    # digest taken now catches an installer that *creates* ~/.claude/plugins as
    # well as one that edits it. A before/after pair around a single later
    # install cannot -- an earlier install would already have put the same bytes
    # there, leaving the pair equal and the assertion green.
    $pristinePlugins = Get-TreeDigest (Join-Path $TmpHome '.claude\plugins')

    Write-Host '=== Fresh install into an empty scratch repo ==='
    $scratch = Join-Path $TmpWork 'repo'
    New-Item -ItemType Directory -Force -Path $scratch | Out-Null
    Invoke-Install -Label 'fresh install' -RepoPath $scratch

    Assert-Exists (Join-Path $TmpHome '.claude\skills\coding-standards\SKILL.md') `
        'baseline coding-standards skill lands at user level'
    Assert-Exists (Join-Path $TmpHome '.claude\skills\backlog-refinement\SKILL.md') `
        'backlog-refinement skill lands at user level'
    Assert-Exists (Join-Path $scratch '.claude\standards.md') `
        'per-repo standards.md is installed'
    Assert-NotExists (Join-Path $scratch '.claude\skills\coding-standards') `
        'project-level coding-standards skill does not come back'
    Assert-NotExists (Join-Path $scratch '.claude\skills\backlog-refinement') `
        'project-level backlog-refinement skill does not come back'
    Assert-Exists (Join-Path $scratch '.claude\skills\implement-sprint') `
        'bulk project-layer copy still lands implement-sprint'
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
    # The mod section is the one part of the installer that could plausibly
    # write outside the two trees above -- ~/.claude/plugins is where Claude
    # Code keeps its own plugin registry, and an installer that decided to
    # "help" would write there. Nothing under skills/ would move if it did, so
    # the dry-run guarantee needs its own digest for that path.
    $homePluginsBefore = Get-TreeDigest (Join-Path $TmpHome '.claude\plugins')
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
    if ($homePluginsBefore -eq (Get-TreeDigest (Join-Path $TmpHome '.claude\plugins'))) {
        Pass 'dry run leaves ~/.claude/plugins unchanged'
    } else {
        Assert-Fail 'dry run leaves ~/.claude/plugins unchanged' 'tree digest changed'
    }
    # Writing nothing is only half the dry-run contract: the mod section reports
    # either way, because what it reports is all it ever does.
    $dryModSection = Join-Path $TmpWork 'mod-section-dry.txt'
    [System.IO.File]::WriteAllText($dryModSection, (Get-ModSection $script:LastInstallLog))
    Assert-LogContains $dryModSection '/plugin install dev-loop-inspector@claude-pen' `
        'dry run still prints the mod enablement commands'

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
    Write-Host '=== Mod: dev-loop-inspector ==='
    # Nothing is copied for the mod. A marketplace whose source is a relative
    # path is read from the bundle folder in place, so the installer's entire
    # job is to verify the vendored tree and print the two enablement commands
    # -- which makes most of what follows an assertion that nothing happened.
    $modDir          = Join-Path $RepoRoot 'plugin\dev-loop-inspector'
    $pluginJson      = Join-Path $modDir '.claude-plugin\plugin.json'
    $marketplaceJson = Join-Path $RepoRoot '.claude-plugin\marketplace.json'

    Assert-Exists $pluginJson `
        'vendored mod carries its plugin manifest'
    Assert-Exists (Join-Path $modDir 'hooks\hooks.json') `
        'vendored mod carries its hooks manifest'
    Assert-Exists (Join-Path $modDir 'hooks\register.tsx') `
        'vendored mod carries its hook source'
    Assert-Exists $marketplaceJson `
        'repository root carries the marketplace manifest'

    # The failure these three guard against is the quiet one: if the marketplace
    # entry and the plugin manifest disagree on the name, /plugin install
    # answers `Plugin "..." not found in marketplace` and nothing else in the
    # bundle shows any symptom. The marketplace's own name is pinned for the
    # same reason -- it is the half after the @ in the command the installer
    # prints below, so a rename there breaks the route while both manifests stay
    # internally consistent.
    #
    # ConvertFrom-Json here where the bash suite has to settle for grep and sed:
    # a parser ships with the shell, so there is nothing to be gained by
    # mirroring that suite's line-oriented shortcut. Both assert the same three
    # values against the same literals, and this side additionally refuses
    # malformed JSON outright.
    $pluginManifest = Get-Content -Raw -LiteralPath $pluginJson      | ConvertFrom-Json
    $marketManifest = Get-Content -Raw -LiteralPath $marketplaceJson | ConvertFrom-Json
    Assert-Equal $pluginManifest.name 'dev-loop-inspector' `
        'plugin manifest names the mod dev-loop-inspector'
    Assert-Equal $marketManifest.plugins[0].name $pluginManifest.name `
        'marketplace entry name matches the plugin manifest name'
    Assert-Equal $marketManifest.name 'claude-pen' `
        'marketplace manifest names the marketplace claude-pen'

    # Enabling a plugin is the user's decision and it is recorded in a settings
    # file, so the installer must leave those alone as firmly as it leaves the
    # registry alone. Both settings files are planted with sentinel bytes before
    # the run, which makes this a non-clobber assertion rather than the weaker
    # non-creation one; settings.local.json is left absent instead, because
    # nothing in the bundle ships one and creating it is the whole risk.
    $modScratch = Join-Path $TmpWork 'mod-repo'
    New-Item -ItemType Directory -Force -Path (Join-Path $modScratch '.claude') | Out-Null
    Write-Sentinel (Join-Path $TmpHome '.claude\settings.json') "$sentinelTag-user-settings"
    Write-Sentinel (Join-Path $modScratch '.claude\settings.json') "$sentinelTag-repo-settings"
    $expectedUserSettings = Join-Path $TmpWork 'expected-user-settings.json'
    $expectedRepoSettings = Join-Path $TmpWork 'expected-repo-settings.json'
    Copy-Item (Join-Path $TmpHome '.claude\settings.json') $expectedUserSettings -Force
    Copy-Item (Join-Path $modScratch '.claude\settings.json') $expectedRepoSettings -Force

    Invoke-Install -Label 'install with the mod present' -RepoPath $modScratch

    Assert-FilesIdentical (Join-Path $TmpHome '.claude\settings.json') $expectedUserSettings `
        'install leaves an existing user-level settings.json byte-identical'
    Assert-NotExists (Join-Path $TmpHome '.claude\settings.local.json') `
        'install creates no user-level settings.local.json'
    Assert-FilesIdentical (Join-Path $modScratch '.claude\settings.json') $expectedRepoSettings `
        'install leaves an existing repo settings.json byte-identical'
    Assert-NotExists (Join-Path $modScratch '.claude\settings.local.json') `
        'install creates no settings.local.json in the target repo'

    # The printed commands are the only output of this section anyone acts on,
    # so they are asserted as literal text. The quotes around the path are part
    # of the contract, not formatting: this bundle's own folder name contains a
    # space, and an unquoted path would split on it. Single quotes rather than
    # double, because a double-quoted path re-enters the shell parser when the
    # line is pasted -- the hostile-path block further down is what pins that
    # down.
    #
    # The positives read the extracted section rather than the whole log, which
    # is what keeps the idempotence comparison below honest: an extraction that
    # matched nothing would compare empty against empty and pass, and these fail
    # on an empty section.
    $modSectionFirst = Join-Path $TmpWork 'mod-section-1.txt'
    [System.IO.File]::WriteAllText($modSectionFirst, (Get-ModSection $script:LastInstallLog))
    Assert-LogContains $modSectionFirst '/plugin install dev-loop-inspector@claude-pen' `
        'install prints the marketplace-qualified /plugin install command'
    Assert-LogContains $modSectionFirst "claude plugin marketplace add '$RepoRoot'" `
        'install prints the marketplace add command with the bundle path quoted'

    # The label is contract text, not decoration: single quotes are right for
    # bash and PowerShell and mean nothing in cmd.exe, where a bundle name
    # carrying one of that shell's separators -- & ^ ( ) -- splits the line and
    # runs the rest. No quoting fixes all three at once, so naming the two this
    # form is for is the only thing standing between the printed line and a
    # cmd.exe paste.
    Assert-LogContains $modSectionFirst '1. in PowerShell (not cmd.exe) --' `
        'install names the shell the printed quoting is correct for'

    # The verdict itself, both halves of it. Without these the branch that
    # decides what the user is told could be inverted, or its needed-file list
    # could name a file that does not exist, and every other assertion here
    # would stay green.
    Assert-LogContains $modSectionFirst 'vendored source and marketplace entry present' `
        'a complete bundle reports the vendored source and marketplace entry present'
    Assert-LogLacks $modSectionFirst '! missing' `
        'a complete bundle names no missing file'

    # `--marketplace <name>` is asserted absent deliberately, and over the whole
    # log rather than the section, since the closing hints talk about the mod
    # too. That flag takes a marketplace *source* -- a path, a URL, owner/repo
    # -- and adds it, so pairing it with the name of a marketplace already added
    # is rejected by the CLI; the valid way to name an added marketplace is
    # <plugin>@<marketplace>. README.md and INSTALL.md legitimately write
    # --marketplace followed by a path, which is why the negative names the
    # invalid pairing and not the flag.
    Assert-LogLacks $script:LastInstallLog '--marketplace claude-pen' `
        'install prints no --marketplace claude-pen, which the CLI rejects'

    $modSectionSecond = Join-Path $TmpWork 'mod-section-2.txt'
    Invoke-Install -Label 're-install with the mod present' -RepoPath $modScratch
    [System.IO.File]::WriteAllText($modSectionSecond, (Get-ModSection $script:LastInstallLog))
    Assert-FilesIdentical $modSectionFirst $modSectionSecond `
        'a second install prints an identical mod section'

    # A partial unzip must cost the user the mod and nothing else. Mutating a
    # bundle is the only way to test that, and the repository under test is
    # never a legitimate thing to mutate, so this runs a copy carrying just what
    # install.ps1 reads: the three layers, the marketplace manifest and the
    # script. docs\ is ~10 MB of PNGs the installer never opens and is left out.
    #
    # Invoke-Install is not used here: it runs the repository's own installer,
    # and the assertion is the exit status itself rather than a filesystem
    # effect, so the status has to be captured instead of unwinding the run.
    $modBundle = Join-Path $TmpWork 'partial-bundle'
    New-Item -ItemType Directory -Force -Path $modBundle | Out-Null
    Copy-Item -LiteralPath $InstallPs1 -Destination (Join-Path $modBundle 'install.ps1')
    foreach ($layer in 'user', 'project', 'plugin', '.claude-plugin') {
        Copy-Item -LiteralPath (Join-Path $RepoRoot $layer) -Destination $modBundle -Recurse
    }
    Remove-Item -LiteralPath (Join-Path $modBundle 'plugin\dev-loop-inspector\hooks\hooks.json') -Force
    $partialScratch = Join-Path $TmpWork 'partial-repo'
    New-Item -ItemType Directory -Force -Path $partialScratch | Out-Null
    $partialLog    = Join-Path $TmpWork 'log-partial-bundle.txt'
    $partialStatus = 0
    $global:LASTEXITCODE = 0
    try {
        & (Join-Path $modBundle 'install.ps1') -Repo $partialScratch *>&1 |
            Out-File -LiteralPath $partialLog -Encoding utf8 -Width 4096
        $partialStatus = $LASTEXITCODE
    } catch {
        $partialStatus = "threw -- $($_.Exception.Message)"
        ($_ | Out-String) | Add-Content -LiteralPath $partialLog
    }

    Assert-Equal $partialStatus 0 `
        'an incomplete mod bundle does not fail the install'
    Assert-LogContains $partialLog '! missing plugin\dev-loop-inspector\hooks\hooks.json' `
        'an incomplete mod bundle names the missing file'
    Assert-LogContains $partialLog 'mod incomplete' `
        'an incomplete mod bundle says the mod is incomplete'

    # The bundle's own directory name is the one part of an install an attacker
    # can choose while leaving the scripts genuine and inspectable, and the
    # installer interpolates it into a command line the user is told to paste.
    # Safe means the paste runs exactly one command, with the real path as its
    # last argument, and nothing else -- so the test pastes it: `claude` is
    # shadowed by a function that records what it was handed, and the payload
    # baked into the directory name would create a marker in the sandbox if it
    # ran. -WhatIfOnly, and a bundle carrying only the script, because how the
    # installer prints its own path is the whole of what is under test here.
    $evilBundle = Join-Path $TmpWork 'evil $(New-Item pwned -ItemType Directory) `n it''s'
    New-Item -ItemType Directory -Force -Path $evilBundle | Out-Null
    Copy-Item -LiteralPath $InstallPs1 -Destination (Join-Path $evilBundle 'install.ps1')
    $evilScratch = Join-Path $TmpWork 'evil-repo'
    New-Item -ItemType Directory -Force -Path $evilScratch | Out-Null
    $evilLog = Join-Path $TmpWork 'log-evil-bundle.txt'
    & (Join-Path $evilBundle 'install.ps1') -Repo $evilScratch -WhatIfOnly *>&1 |
        Out-File -LiteralPath $evilLog -Encoding utf8 -Width 4096

    $pasteSandbox = Join-Path $TmpWork 'paste-sandbox'
    New-Item -ItemType Directory -Force -Path $pasteSandbox | Out-Null
    $script:PasteArgs = Join-Path $TmpWork 'paste-args.txt'
    [System.IO.File]::WriteAllText($script:PasteArgs, '')
    function claude { [System.IO.File]::WriteAllText($script:PasteArgs, ($args -join '|')) }
    # One line, so a path containing a newline is outside this check -- as it is
    # outside NTFS, where the suite's own bundle lives.
    $pasteLine = [System.IO.File]::ReadAllLines($evilLog) |
        Where-Object { $_.Contains('claude plugin marketplace add') } |
        Select-Object -First 1
    $pasteStatus = 0
    Push-Location -LiteralPath $pasteSandbox
    try     { Invoke-Expression $pasteLine }
    catch   { $pasteStatus = "threw -- $($_.Exception.Message)" }
    finally { Pop-Location; Remove-Item -LiteralPath 'function:claude' }

    Assert-Equal $pasteStatus 0 `
        'the printed add command parses as one command when pasted'
    Assert-NotExists (Join-Path $pasteSandbox 'pwned') `
        'pasting the printed add command runs nothing hidden in the bundle path'
    Assert-Equal (Get-Content -Raw -LiteralPath $script:PasteArgs) "plugin|marketplace|add|$evilBundle" `
        'the pasted add command receives the bundle path exactly as it is on disk'

    # The paste above went into the shell that printed the line. This one goes
    # into cmd.exe, the third shell on this platform and the one the printed
    # quoting is *not* right for -- it treats ' as an ordinary character, so a
    # bundle name carrying & or ^ would split the line there and run the rest.
    # Nothing in the quoting can fix that for all three shells at once, which is
    # what the step-1 label asserted above exists to say; what is pinned here is
    # the other half, that the line the installer does print is inert in cmd.exe
    # for the hostile name above and arrives whole. Without this the suite would
    # only ever paste into its own shell. `claude` is a .cmd recorder on PATH
    # rather than a function because cmd.exe cannot see a PowerShell function.
    $cmdStub = Join-Path $TmpWork 'cmd-stub'
    New-Item -ItemType Directory -Force -Path $cmdStub | Out-Null
    # %* is the raw argument tail, so the record shows what cmd.exe handed the
    # command: the whole quoted path, or whatever is left of it after a split.
    Set-Content -LiteralPath (Join-Path $cmdStub 'claude.cmd') -Encoding ascii -Value @(
        '@echo off',
        '>"%DLI_PASTE_RECORD%" echo %*')
    $cmdSandbox = Join-Path $TmpWork 'cmd-paste-sandbox'
    New-Item -ItemType Directory -Force -Path $cmdSandbox | Out-Null
    $cmdRecord = Join-Path $TmpWork 'cmd-paste-args.txt'
    [System.IO.File]::WriteAllText($cmdRecord, '')
    $env:DLI_PASTE_RECORD = $cmdRecord
    $savedPath = $env:PATH
    $env:PATH  = $cmdStub + [System.IO.Path]::PathSeparator + $savedPath
    Push-Location -LiteralPath $cmdSandbox
    # Through stdin, which parses as an interactive paste does rather than as a
    # batch file. /Q so the echoed prompt does not reach the record.
    try     { $pasteLine | cmd.exe /Q 2>&1 | Out-Null }
    finally {
        Pop-Location
        $env:PATH = $savedPath
        Remove-Item -LiteralPath 'Env:DLI_PASTE_RECORD'
    }
    $cmdDelivered = [System.IO.File]::ReadAllText($cmdRecord).TrimEnd("`r", "`n")
    $cmdExpected  = "plugin marketplace add '" + $evilBundle.Replace("'", "''") + "'"
    # Any entry at all, not a named marker: cmd.exe keeps the quote characters
    # it does not understand, so a command that did split out of the printed
    # line would create `pwned'` rather than `pwned`.
    $cmdLeftovers = (Get-ChildItem -LiteralPath $cmdSandbox -Force | ForEach-Object { $_.Name }) -join ','

    Assert-Equal $cmdLeftovers '' `
        'pasting the printed add command into cmd.exe creates nothing in the pasting directory'
    Assert-Equal $cmdDelivered $cmdExpected `
        'cmd.exe hands the add command the whole printed path, unsplit'

    # Last, so it speaks for every install this run made: the mod is enabled
    # through Claude Code's own registry under ~/.claude/plugins, which is that
    # program's cache and not an install target, and the digest is compared
    # against the one taken while $TmpHome was still pristine. Whatever it was
    # then -- MISSING, in a scratch HOME -- is what it has to be now.
    Assert-Equal (Get-TreeDigest (Join-Path $TmpHome '.claude\plugins')) $pristinePlugins `
        'no install writes anything under ~/.claude/plugins'

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
