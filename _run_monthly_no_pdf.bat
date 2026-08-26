@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo Starten CSAT-Compass maandelijkse run...
set PYTHONIOENCODING=utf-8
.venv\Scripts\python.exe scripts\run_monthly.py > _run_log.txt 2>&1
IF ERRORLEVEL 1 (
    echo SQL-fout of andere fout gedetecteerd, opnieuw proberen met --force-csv...
    set PYTHONIOENCODING=utf-8
    .venv\Scripts\python.exe scripts\run_monthly.py --force-csv >> _run_log.txt 2>&1
)
echo Klaar. Resultaat in _run_log.txt
