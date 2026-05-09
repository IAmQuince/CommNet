@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
set "PYTHONPATH=%ROOT%src;%PYTHONPATH%"
set "PYEXE="
where py >nul 2>nul
if %ERRORLEVEL%==0 (set "PYEXE=py -3") else (where python >nul 2>nul & if %ERRORLEVEL%==0 set "PYEXE=python")
if "%PYEXE%"=="" (echo Python was not found.& pause& exit /b 1)
echo Starting CommNet Control Window...
echo Keep the control window open/minimized while the server is running.
%PYEXE% "%ROOT%src\commnet\main.py" controller
if not %ERRORLEVEL%==0 pause
