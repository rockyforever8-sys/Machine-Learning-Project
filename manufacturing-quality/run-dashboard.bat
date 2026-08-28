@echo off
if /i not "%~1"=="INTERNAL" (
  start "PPAP Dashboard" cmd /k ""%~f0" INTERNAL"
  exit /b
)

setlocal EnableExtensions
cd /d "%~dp0"
set "LOG=%~dp0dashboard-launch.log"

echo.
echo  PPAP Level 3 Dashboard Launcher
echo  ===============================
echo.

set "PY="
where py >nul 2>&1 && set "PY=py"
if not defined PY where python >nul 2>&1 && set "PY=python"
if not defined PY if exist "C:\Program Files\Python313\python.exe" set "PY=C:\Program Files\Python313\python.exe"
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"

if not defined PY (
  echo ERROR: Python not found.
  pause
  exit /b 1
)

echo Using: %PY%
echo.

echo Installing dependencies...
"%PY%" -m pip install --user "streamlit>=1.32" "pypdf>=4.0"
if errorlevel 1 (
  echo ERROR: pip install failed.
  pause
  exit /b 1
)

echo.
"%PY%" "%~dp0launch_dashboard.py"
set "RC=%ERRORLEVEL%"

if %RC% neq 0 (
  echo.
  echo Dashboard failed. Check: %LOG%
  pause
  exit /b %RC%
)

pause
exit /b 0
