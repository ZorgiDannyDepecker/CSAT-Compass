# tools/lint.ps1
# CSAT-Compass — volledige kwaliteitscontrole
#
# Gebruik: .\tools\lint.ps1
# Optie:   .\tools\lint.ps1 -Fix   (automatisch herstelbare issues fixen)
#
# Dekt dezelfde checks als pre-commit, maar manueel uit te voeren.
# pre-commit (automatische gate bij git commit) vereist installatie
# buiten ZORGI-netwerk: python -m pre_commit install

param(
    [switch]$Fix
)

$ErrorCount = 0

Write-Host "`n=============================" -ForegroundColor Cyan
Write-Host " CSAT-Compass — Lint check" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

# --- [1/5] Ruff: linting ---
Write-Host "`n[1/5] Ruff — linting..." -ForegroundColor Yellow
if ($Fix) {
    python -m ruff check src/ tests/ --fix
} else {
    python -m ruff check src/ tests/ --output-format=concise
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "      Ruff: issues gevonden." -ForegroundColor Red
    $ErrorCount++
} else {
    Write-Host "      Ruff: alles in orde." -ForegroundColor Green
}

# --- [2/5] Ruff: opmaak + regellengte (max 100) ---
Write-Host "`n[2/5] Ruff — opmaak en regellengte (max 100)..." -ForegroundColor Yellow
if ($Fix) {
    python -m ruff format src/ tests/
} else {
    python -m ruff format src/ tests/ --check
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "      Opmaak: afwijkingen gevonden." -ForegroundColor Red
    Write-Host "      Tip: '.\tools\lint.ps1 -Fix' past automatisch aan." -ForegroundColor Yellow
    $ErrorCount++
} else {
    Write-Host "      Opmaak: alles in orde." -ForegroundColor Green
}

# --- [3/5] Mypy: typecontrole ---
Write-Host "`n[3/5] Mypy — typecontrole..." -ForegroundColor Yellow
python -m mypy src/ --ignore-missing-imports --no-error-summary 2>&1 | Where-Object { $_ -notmatch "^Found" }
if ($LASTEXITCODE -ne 0) {
    Write-Host "      Mypy: typefouten gevonden." -ForegroundColor Red
    $ErrorCount++
} else {
    Write-Host "      Mypy: geen typefouten." -ForegroundColor Green
}

# --- [4/5] Bandit: security scan ---
Write-Host "`n[4/5] Bandit — security scan..." -ForegroundColor Yellow
python -m bandit -r src/ -ll -q 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "      Bandit: security issues gevonden." -ForegroundColor Red
    $ErrorCount++
} else {
    Write-Host "      Bandit: geen security issues." -ForegroundColor Green
}

# --- [5/5] pip-audit: CVE-controle dependencies ---
Write-Host "`n[5/5] pip-audit — CVE-controle..." -ForegroundColor Yellow
# pip-audit raadpleegt de externe PyPI/OSV-CVE-database.
# Op het ZORGI-netwerk onderschept de corporate proxy de SSL-verbinding
# (self-signed certificaat) waardoor de verbinding wordt geweigerd.
# Dit is normaal gedrag — geen fout in het project.
# Alternatief: GitHub Copilot voert CVE-checks in-session uit via ingebouwde tooling.
$auditOutput = python -m pip_audit --local --desc 2>&1
$auditExit = $LASTEXITCODE
$isSslError = ($auditOutput | Out-String) -match "SSLError|CERTIFICATE_VERIFY_FAILED|ConnectionReset"

if ($auditExit -ne 0 -and $isSslError) {
    Write-Host "      pip-audit: overgeslagen — ZORGI corporate proxy blokkeert SSL naar pypi.org." -ForegroundColor DarkYellow
    Write-Host "      Alternatief: typ '/cve' in GitHub Copilot Chat — werkt proxy-proof via ingebouwde CVE-tooling." -ForegroundColor DarkYellow
    Write-Host "      Of: voer pip-audit uit via hotspot / thuis / buiten ZORGI-netwerk." -ForegroundColor DarkYellow
} elseif ($auditExit -ne 0) {
    Write-Host "      pip-audit: kwetsbare packages gevonden." -ForegroundColor Red
    $auditOutput | Write-Host
    $ErrorCount++
} else {
    Write-Host "      pip-audit: geen kwetsbaarheden gevonden." -ForegroundColor Green
}

# --- Samenvatting ---
Write-Host "`n=============================" -ForegroundColor Cyan
if ($ErrorCount -eq 0) {
    Write-Host " Alle checks geslaagd." -ForegroundColor Green
} else {
    Write-Host " $ErrorCount check(s) mislukt." -ForegroundColor Red
    Write-Host " Tip: voer '.\tools\lint.ps1 -Fix' uit voor automatische fixes." -ForegroundColor Yellow
}
Write-Host "=============================" -ForegroundColor Cyan

