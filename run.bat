@echo off
title PRW-Wild 3D Digital Twin Launcher
cd /d "%~dp0"
set PYTHONPATH=src
echo ========================================================
echo   Launching PRW-Wild 3D Digital Twin & Hardware Lab
echo   URL: http://127.0.0.1:8000/
echo ========================================================
python -m prw_wild.web --port 8000 --open
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Trying with py launcher...
    py -m prw_wild.web --port 8000 --open
)
pause
