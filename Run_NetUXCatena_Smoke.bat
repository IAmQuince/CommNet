@echo off
setlocal
cd /d "%~dp0"
py -3 tools\smoke\run_node_identity_smoke.py
py -3 tools\smoke\run_catena_protocol_smoke.py
py -3 tools\smoke\run_fake_catena_smoke.py
pause
