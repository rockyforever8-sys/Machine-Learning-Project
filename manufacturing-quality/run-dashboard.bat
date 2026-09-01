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

if not exist "%~dp0launch_dashboard.py" (
  echo launch_dashboard.py is missing. Downloading from GitHub...
  curl.exe -L --fail -o "%~dp0launch_dashboard.py" "https://raw.githubusercontent.com/rockyforever8-sys/Machine-Learning-Project/main/manufacturing-quality/launch_dashboard.py"
)

if exist "%~dp0launch_dashboard.py" (
  "%PY%" "%~dp0launch_dashboard.py"
  set "RC=%ERRORLEVEL%"
) else if exist "%~dp0dashboard\app.py" (
  echo WARNING: Could not download launch_dashboard.py.
  echo Starting Streamlit directly instead.
  echo.
  "%PY%" -m streamlit run "%~dp0dashboard\app.py" --server.port 8501 --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false
  set "RC=%ERRORLEVEL%"
) else (
  echo ERROR: Dashboard files are missing from this folder:
  echo   %CD%
  echo.
  echo Paste these commands in this window:
  echo   cd ..
  echo   git fetch origin main
  echo   git checkout origin/main -- manufacturing-quality
  echo   cd manufacturing-quality
  echo   run-dashboard.bat
  echo.
  pause
  exit /b 1
)

if !RC! neq 0 (
  echo.
  echo Dashboard failed. Check: %LOG%
  pause
  exit /b !RC!
)

pause
exit /b 0
