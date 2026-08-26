@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ============================================== >> _run_log.txt
echo [Deel A] Maandelijkse run gestart: %date% %time% >> _run_log.txt
echo ============================================== >> _run_log.txt

REM --- Stap 1: matrix + evolutie genereren (alle pijlers, NL+FR) ---
echo Starten CSAT-Compass maandelijkse run...
set PYTHONIOENCODING=utf-8
.venv\Scripts\python.exe scripts\run_monthly.py >> _run_log.txt 2>&1
IF ERRORLEVEL 1 (
    echo SQL-fout of andere fout gedetecteerd, opnieuw proberen met --force-csv... >> _run_log.txt
    set PYTHONIOENCODING=utf-8
    .venv\Scripts\python.exe scripts\run_monthly.py --force-csv >> _run_log.txt 2>&1
    IF ERRORLEVEL 1 (
        echo [FOUT] run_monthly.py definitief mislukt - Deel A afgebroken, geen PDF-conversie. >> _run_log.txt
        exit /b 1
    )
)

REM --- Stap 2: datum van vandaag bepalen, locale-onafhankelijk via PowerShell ---
for /f %%d in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set "VANDAAG=%%d"

REM --- Stap 3: PDF-conversie van alle .md + .png in de datummap van vandaag ---
echo PDF-conversie starten voor output\%VANDAAG%... >> _run_log.txt
.venv\Scripts\python.exe "C:\Users\danndepe\Documents\AI\Q&A-Lab\code\md_to_pdf.py" -r "output\%VANDAAG%" >> _run_log.txt 2>&1
IF ERRORLEVEL 1 (
    echo [FOUT] PDF-conversie mislukt voor output\%VANDAAG% >> _run_log.txt
    exit /b 1
)

echo [Deel A] Klaar. Resultaat in output\%VANDAAG%\ en _run_log.txt >> _run_log.txt
echo Klaar. Resultaat in output\%VANDAAG%\ en _run_log.txt
