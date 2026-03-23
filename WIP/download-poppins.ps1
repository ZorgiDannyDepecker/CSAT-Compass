# download-poppins.ps1
# Download Poppins Light (300) en ExtraBold (800) naar src/static/fonts/
# Run vanuit de CSAT-Compass projectroot:
#   .\WIP\download-poppins.ps1

$fontsDir = "src\static\fonts"
if (-not (Test-Path $fontsDir)) { New-Item -ItemType Directory -Path $fontsDir -Force | Out-Null }

$baseUrl = "https://github.com/google/fonts/raw/main/ofl/poppins"
$fonts = @{
    "Poppins-Light.ttf"     = "$baseUrl/Poppins-Light.ttf"
    "Poppins-ExtraBold.ttf" = "$baseUrl/Poppins-ExtraBold.ttf"
}

foreach ($f in $fonts.GetEnumerator()) {
    $dest = Join-Path $fontsDir $f.Key
    Write-Host "Downloading $($f.Key)..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $f.Value -OutFile $dest -UseBasicParsing
    Write-Host "  -> $dest ($((Get-Item $dest).Length / 1KB -as [int]) KB)" -ForegroundColor Green
}

Write-Host "`nDone! Fonts opgeslagen in $fontsDir" -ForegroundColor Yellow
