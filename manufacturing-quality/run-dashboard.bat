@echo off
if /i not "%~1"=="INTERNAL" (
  start "PPAP Dashboard" cmd /k ""%~f0" INTERNAL"
  exit /b
)

setlocal EnableExtensions EnableDelayedExpansion
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

if exist "%~dp0launch_dashboard.py" (
  "%PY%" "%~dp0launch_dashboard.py"
  set "RC=%ERRORLEVEL%"
) else if exist "%~dp0dashboard\app.py" (
  echo WARNING: launch_dashboard.py is missing.
  echo Starting Streamlit directly instead.
  echo If this folder is incomplete, run: git checkout main ^&^& git pull
  echo.
  "%PY%" -m streamlit run "%~dp0dashboard\app.py" --server.port 8501 --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false
  set "RC=%ERRORLEVEL%"
) else (
  echo ERROR: Dashboard files are missing from this folder:
  echo   %CD%
  echo.
  echo Expected:
  echo   launch_dashboard.py
  echo   dashboard\app.py
  echo.
  echo Fix: open Git Bash in Machine-Learning-Project and run:
  echo   git checkout main
  echo   git pull
  echo Then open manufacturing-quality and start the dashboard again.
  echo.
  pause
  exit /b 1
)

if %RC% neq 0 (
  echo.
  echo Dashboard failed. Check: %LOG%
  pause
  exit /b %RC%
)

pause
exit /b 0
