@echo off
setlocal
cd /d "%~dp0"
set PYTHONPATH=%CD%\src
python tools\dev\run_usability_hud_acceptance.py
pause
