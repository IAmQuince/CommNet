@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
set "PYTHONPATH=%ROOT%src;%PYTHONPATH%"
set "PYEXE="
where py >nul 2>nul
if %ERRORLEVEL%==0 (set "PYEXE=py -3") else (where python >nul 2>nul & if %ERRORLEVEL%==0 set "PYEXE=python")
if "%PYEXE%"=="" (echo Python was not found.& pause& exit /b 1)
%PYEXE% "%ROOT%src\commnet\main.py" launch --page admin
if not %ERRORLEVEL%==0 pause
