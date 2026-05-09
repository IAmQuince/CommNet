@echo off
setlocal
cd /d %~dp0
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 tools\smoke\run_quickshare_smoke.py
) else (
  python tools\smoke\run_quickshare_smoke.py
)
echo.
echo QuickShare smoke test complete. Press any key to close.
pause >nul
