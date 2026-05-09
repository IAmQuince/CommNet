@echo off
setlocal
cd /d "%~dp0"

python tools\audit\check_dependencies.py || goto fail
python tools\audit\check_install_profiles.py || goto fail
python tools\audit\check_transport_registry.py || goto fail
python tools\audit\check_route_policy.py || goto fail
python tools\audit\check_resource_limits.py || goto fail
python tools\audit\check_no_false_wheels.py || goto fail

echo.
echo CommNet backbone requirements audits completed.
pause
exit /b 0

:fail
echo.
echo CommNet backbone requirements audit reported issues.
pause
exit /b 1
