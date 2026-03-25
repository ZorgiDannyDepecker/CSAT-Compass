# sync-design-system.ps1
# Kopieert de ZORGI Design System golden source naar de lokale read-only kopie.
#
# Conventie: PHARMA-Conventions\pharma\project-conventies.md §12.3
# Golden source: PHARMA-Conventions\zorgi\zorgi_design_system.md
# Doel:         .github\docs\zorgi_design_system.md (read-only kopie — nooit rechtstreeks bewerken)
#
# Gebruik:
#   .\tools\sync-design-system.ps1
#
# Na uitvoering: commit de bijgewerkte kopie via /git
$bron = "C:\Users\danndepe\Documents\AI\PHARMA-Conventions\zorgi\zorgi_design_system.md"
$projectRoot = Split-Path $PSScriptRoot -Parent
$doel = Join-Path $projectRoot ".github\docs\zorgi_design_system.md"
if (-not (Test-Path $bron)) {
    Write-Error "[FOUT] Golden source niet gevonden: $bron"
    exit 1
}
$doelMap = Split-Path $doel -Parent
if (-not (Test-Path $doelMap)) {
    New-Item -ItemType Directory -Path $doelMap -Force | Out-Null
}
Copy-Item -Path $bron -Destination $doel -Force
$tijdstip = Get-Date -Format "dd/MM/yyyy HH:mm"
Write-Host "[OK] zorgi_design_system.md gesynchroniseerd ($tijdstip)"
Write-Host "     Van: $bron"
Write-Host "     Naar: $doel"
Write-Host ""
Write-Host "Volgende stap: commit de bijgewerkte kopie via /git"
