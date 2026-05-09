@echo off
setlocal
cd /d %~dp0
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 tools\smoke\run_network_smoke.py
) else (
  python tools\smoke\run_network_smoke.py
)
echo.
echo Network smoke test complete. Press any key to close.
pause >nul
