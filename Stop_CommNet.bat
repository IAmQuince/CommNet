@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
set "PYTHONPATH=%ROOT%src;%PYTHONPATH%"
set "PYEXE="
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  set "PYEXE=py -3"
) else (
  where python >nul 2>nul
  if %ERRORLEVEL%==0 set "PYEXE=python"
)
if "%PYEXE%"=="" (
  echo Python was not found.
  echo Install Python 3, then re-run this file.
  echo Download from https://www.python.org/ on an internet-connected machine if needed.
  pause
  exit /b 1
)

echo Stopping CommNet server...
%PYEXE% "%ROOT%src\commnet\main.py" stop
if not %ERRORLEVEL%==0 pause
