@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
set "PYTHONPATH=%ROOT%src;%PYTHONPATH%"
set "PYEXE="
where py >nul 2>nul
if %ERRORLEVEL%==0 (set "PYEXE=py -3") else (where python >nul 2>nul & if %ERRORLEVEL%==0 set "PYEXE=python")
if "%PYEXE%"=="" (echo Python was not found.& pause& exit /b 1)
%PYEXE% "%ROOT%tools\dev\run_default_admin_smoke.py" || goto fail
%PYEXE% "%ROOT%tools\dev\run_admin_boundary_smoke.py" || goto fail
%PYEXE% "%ROOT%tools\dev\run_shell_separation_smoke.py" || goto fail
%PYEXE% "%ROOT%tools\dev\run_account_dropdown_smoke.py" || goto fail
%PYEXE% "%ROOT%tools\dev\run_user_settings_route_smoke.py" || goto fail
%PYEXE% "%ROOT%tools\dev\run_portal_grid_smoke.py" || goto fail
%PYEXE% "%ROOT%tools\dev\run_bbs_thread_smoke.py" || goto fail
%PYEXE% "%ROOT%tools\dev\run_retroweb_social_smoke.py" || goto fail
%PYEXE% "%ROOT%tools\dev\run_meshtastic_dependency_smoke.py" || goto fail
%PYEXE% "%ROOT%tools\dev\run_meshtastic_fake_smoke.py" || goto fail
echo ServiceTrayMesh smoke PASS
exit /b 0
:fail
echo ServiceTrayMesh smoke FAILED
pause
exit /b 2
