@echo off
setlocal
cd /d "%~dp0"
py -3 tools\smoke\run_netpath_catena_regression_smoke.py 2>nul || python tools\smoke\run_netpath_catena_regression_smoke.py
pause
