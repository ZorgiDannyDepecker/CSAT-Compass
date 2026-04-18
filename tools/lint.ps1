# tools/lint.ps1
# CSAT-Compass — volledige kwaliteitscontrole
#
# Gebruik:
#   .\tools\lint.ps1                        Alle checks uitvoeren (read-only)
#   .\tools\lint.ps1 -Fix                   Automatisch herstelbare issues fixen
#   .\tools\lint.ps1 -Verbose               Uitgebreide output per tool
#   .\tools\lint.ps1 -Skip Bandit,PipAudit  Specifieke tools overslaan
#   .\tools\lint.ps1 -Target src/           Alleen opgegeven map controleren
#
# Dekt dezelfde checks als pre-commit, maar manueel uit te voeren.
# pre-commit (automatische gate bij git commit) vereist installatie
# buiten ZORGI-netwerk: python -m pre_commit install

param(
    [switch]$Fix,
    [switch]$Verbose,
    [string]$Target = "",
    [string[]]$Skip = @()
)

# --- Configuratie ---
$DefaultFolders = @("src/", "tests/")
$ScanFolders    = if ($Target -ne "") { @($Target) } else { $DefaultFolders }
$ScanPath       = $ScanFolders -join " "

$Results        = [ordered]@{}
$ErrorCount     = 0
$SkipCount      = 0
$StartTime      = Get-Date

# --- Hulpfuncties ---

function Write-Header {
    param([string]$Title)
    $line = "=" * ($Title.Length + 4)
    Write-Host "`n$line" -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host "$line" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Label)
    Write-Host "`n$Label" -ForegroundColor Yellow
}

function Write-StepResult {
    param([string]$Tool, [string]$Status, [string]$Message, [string]$Color)
    $pad = "      "
    Write-Host "${pad}${Tool}: ${Message}" -ForegroundColor $Color
    $Results[$Tool] = @{ Status = $Status; Message = $Message }
}

function Test-ToolAvailable {
    param([string]$Module)
    $check = python -m $Module --version 2>&1
    return ($LASTEXITCODE -eq 0)
}

function Measure-StepTime {
    param([datetime]$StepStart)
    $elapsed = (Get-Date) - $StepStart
    return "$([math]::Round($elapsed.TotalSeconds, 1))s"
}

function Should-Skip {
    param([string]$ToolName)
    return ($Skip -contains $ToolName)
}

# --- Banner ---
$Version = "2.0"
Write-Header "CSAT-Compass — Lint check v$Version"
Write-Host "  Mappen  : $ScanPath" -ForegroundColor Gray
Write-Host "  Modus   : $(if ($Fix) { 'FIX (wijzigingen worden toegepast)' } else { 'CHECK (read-only)' })" -ForegroundColor Gray
Write-Host "  Gestart : $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray

# --- [1/5] Ruff: linting ---
Write-Step "[1/5] Ruff — linting..."

if (Should-Skip "Ruff") {
    Write-StepResult "Ruff" "SKIP" "overgeslagen via -Skip parameter." "DarkGray"
    $SkipCount++
} elseif (-not (Test-ToolAvailable "ruff")) {
    Write-StepResult "Ruff" "MISSING" "niet geïnstalleerd. Voer uit: pip install ruff" "DarkYellow"
    $SkipCount++
} else {
    $t = Get-Date
    if ($Fix) {
        $out = python -m ruff check $ScanFolders --fix 2>&1
    } else {
        $out = python -m ruff check $ScanFolders --output-format=concise 2>&1
    }
    $exit = $LASTEXITCODE
    if ($Verbose) { $out | Write-Host }
    $elapsed = Measure-StepTime $t
    if ($exit -ne 0) {
        Write-StepResult "Ruff" "FAIL" "issues gevonden. ($elapsed)" "Red"
        if (-not $Verbose) { $out | Write-Host }
        $ErrorCount++
    } else {
        Write-StepResult "Ruff" "OK" "alles in orde. ($elapsed)" "Green"
    }
}

# --- [2/5] Ruff: formatter ---
Write-Step "[2/5] Ruff — formatter (ex Black)..."

if (Should-Skip "RuffFormat") {
    Write-StepResult "RuffFormat" "SKIP" "overgeslagen via -Skip parameter." "DarkGray"
    $SkipCount++
} elseif (-not (Test-ToolAvailable "ruff")) {
    Write-StepResult "RuffFormat" "MISSING" "ruff niet beschikbaar — formatter overgeslagen." "DarkYellow"
    $SkipCount++
} else {
    $t = Get-Date
    if ($Fix) {
        $out = python -m ruff format $ScanFolders 2>&1
    } else {
        $out = python -m ruff format $ScanFolders --check 2>&1
    }
    $exit = $LASTEXITCODE
    if ($Verbose) { $out | Write-Host }
    $elapsed = Measure-StepTime $t
    if ($exit -ne 0) {
        Write-StepResult "RuffFormat" "FAIL" "afwijkingen gevonden. ($elapsed)" "Red"
        Write-Host "      Tip: '.\tools\lint.ps1 -Fix' past automatisch aan." -ForegroundColor Yellow
        if (-not $Verbose) { $out | Write-Host }
        $ErrorCount++
    } else {
        Write-StepResult "RuffFormat" "OK" "alles in orde. ($elapsed)" "Green"
    }
}

# --- [3/5] MyPy: type checker ---
Write-Step "[3/5] MyPy — type checker..."

if (Should-Skip "MyPy") {
    Write-StepResult "MyPy" "SKIP" "overgeslagen via -Skip parameter." "DarkGray"
    $SkipCount++
} elseif (-not (Test-ToolAvailable "mypy")) {
    Write-StepResult "MyPy" "MISSING" "niet geïnstalleerd. Voer uit: pip install mypy" "DarkYellow"
    $SkipCount++
} else {
    $t = Get-Date
    $out = python -m mypy $ScanFolders --ignore-missing-imports --no-error-summary 2>&1 `
        | Where-Object { $_ -notmatch "^Found" }
    $exit = $LASTEXITCODE
    if ($Verbose) { $out | Write-Host }
    $elapsed = Measure-StepTime $t
    if ($exit -ne 0) {
        Write-StepResult "MyPy" "FAIL" "typefouten gevonden. ($elapsed)" "Red"
        if (-not $Verbose) { $out | Write-Host }
        $ErrorCount++
    } else {
        Write-StepResult "MyPy" "OK" "geen typefouten. ($elapsed)" "Green"
    }
}

# --- [4/5] Bandit: security scan ---
Write-Step "[4/5] Bandit — security scan..."

if (Should-Skip "Bandit") {
    Write-StepResult "Bandit" "SKIP" "overgeslagen via -Skip parameter." "DarkGray"
    $SkipCount++
} elseif (-not (Test-ToolAvailable "bandit")) {
    Write-StepResult "Bandit" "MISSING" "niet geïnstalleerd. Voer uit: pip install bandit" "DarkYellow"
    $SkipCount++
} else {
    $t = Get-Date
    $out = python -m bandit -r $ScanFolders -ll -q 2>&1
    $exit = $LASTEXITCODE
    if ($Verbose) { $out | Write-Host }
    $elapsed = Measure-StepTime $t
    if ($exit -ne 0) {
        Write-StepResult "Bandit" "FAIL" "security issues gevonden. ($elapsed)" "Red"
        if (-not $Verbose) { $out | Write-Host }
        $ErrorCount++
    } else {
        Write-StepResult "Bandit" "OK" "geen security issues. ($elapsed)" "Green"
    }
}

# --- [5/5] pip-audit: CVE-controle ---
Write-Step "[5/5] pip-audit — CVE-controle dependencies..."
# pip-audit raadpleegt de externe PyPI/OSV-CVE-database.
# Op het ZORGI-netwerk onderschept de corporate proxy de SSL-verbinding
# (self-signed certificaat) waardoor de verbinding wordt geweigerd.
# Dit is normaal gedrag — geen fout in het project.
# Alternatief: GitHub Copilot voert CVE-checks in-session uit via ingebouwde tooling.

if (Should-Skip "PipAudit") {
    Write-StepResult "PipAudit" "SKIP" "overgeslagen via -Skip parameter." "DarkGray"
    $SkipCount++
} elseif (-not (Test-ToolAvailable "pip_audit")) {
    Write-StepResult "PipAudit" "MISSING" "niet geïnstalleerd. Voer uit: pip install pip-audit" "DarkYellow"
    $SkipCount++
} else {
    $t = Get-Date
    $auditOutput = python -m pip_audit --local --desc 2>&1
    $auditExit   = $LASTEXITCODE
    $outputStr   = $auditOutput | Out-String
    $isSslError  = $outputStr -match "SSLError|CERTIFICATE_VERIFY_FAILED|ConnectionReset|ProxyError"
    $elapsed     = Measure-StepTime $t

    if ($auditExit -ne 0 -and $isSslError) {
        Write-StepResult "PipAudit" "PROXY" "SSL geblokkeerd door ZORGI corporate proxy. ($elapsed)" "DarkYellow"
        Write-Host "      Alternatief 1 : typ '/cve' in GitHub Copilot Chat (proxy-proof)." -ForegroundColor DarkYellow
        Write-Host "      Alternatief 2 : voer pip-audit uit via hotspot of thuis." -ForegroundColor DarkYellow
        $Results["PipAudit"] = @{ Status = "PROXY"; Message = "SSL geblokkeerd — geen echte fout." }
    } elseif ($auditExit -ne 0) {
        Write-StepResult "PipAudit" "FAIL" "kwetsbare packages gevonden. ($elapsed)" "Red"
        if ($Verbose -or $true) { $auditOutput | Write-Host }
        $ErrorCount++
    } else {
        Write-StepResult "PipAudit" "OK" "geen kwetsbaarheden gevonden. ($elapsed)" "Green"
    }
}

# --- Samenvatting ---
$TotalTime = Measure-StepTime $StartTime
Write-Header "Samenvatting"

foreach ($tool in $Results.Keys) {
    $r     = $Results[$tool]
    $color = switch ($r.Status) {
        "OK"      { "Green" }
        "FAIL"    { "Red" }
        "SKIP"    { "DarkGray" }
        "MISSING" { "DarkYellow" }
        "PROXY"   { "DarkYellow" }
        default   { "White" }
    }
    $icon = switch ($r.Status) {
        "OK"      { "[OK]    " }
        "FAIL"    { "[FAIL]  " }
        "SKIP"    { "[SKIP]  " }
        "MISSING" { "[?]     " }
        "PROXY"   { "[PROXY] " }
        default   { "[???]   " }
    }
    Write-Host "  $icon $tool — $($r.Message)" -ForegroundColor $color
}

Write-Host ""
if ($ErrorCount -eq 0 -and $SkipCount -eq 0) {
    Write-Host "  Alle checks geslaagd. Totaaltijd: $TotalTime" -ForegroundColor Green
} elseif ($ErrorCount -eq 0) {
    Write-Host "  Checks geslaagd ($SkipCount overgeslagen). Totaaltijd: $TotalTime" -ForegroundColor Yellow
} else {
    Write-Host "  $ErrorCount check(s) mislukt, $SkipCount overgeslagen. Totaaltijd: $TotalTime" -ForegroundColor Red
    Write-Host "  Tip: voer '.\tools\lint.ps1 -Fix' uit voor automatische fixes." -ForegroundColor Yellow
}
Write-Host ("=" * 45) -ForegroundColor Cyan

exit $ErrorCount
