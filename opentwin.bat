@echo off
:: PRW-Wild Digital Twin - Quick Launcher and Shortest Terminal View
setlocal

set SCRIPT=D:\Simulation For DT\prw-wild-digital-twin\tools\opentwin.py
set VENV_PY=D:\Simulation For DT\venv\Scripts\python.exe

if exist "%VENV_PY%" (
    "%VENV_PY%" "%SCRIPT%" %*
) else (
    python "%SCRIPT%" %*
)
