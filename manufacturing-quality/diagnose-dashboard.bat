@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo PPAP Dashboard Diagnostics
echo =========================
echo.

set "PY="
where py >nul 2>&1 && set "PY=py"
if not defined PY where python >nul 2>&1 && set "PY=python"
if not defined PY if exist "C:\Program Files\Python313\python.exe" set "PY=C:\Program Files\Python313\python.exe"

if not defined PY (
  echo [FAIL] Python not found
  goto :end
)

echo [OK] Python: %PY%
"%PY%" --version

echo.
echo Checking packages...
"%PY%" -c "import streamlit; print('[OK] streamlit', streamlit.__version__)"
if errorlevel 1 echo [FAIL] streamlit not installed

"%PY%" -c "import pypdf; print('[OK] pypdf', pypdf.__version__)"
if errorlevel 1 echo [FAIL] pypdf not installed

echo.
echo Checking PPAP module...
"%PY%" -c "import sys; sys.path.insert(0, '.'); from ppap_inbox_triage.triage import triage_inbox; print('[OK] ppap_inbox_triage')"
if errorlevel 1 echo [FAIL] ppap_inbox_triage import failed

echo.
echo Checking dashboard app...
if exist "%~dp0dashboard\app.py" (echo [OK] dashboard\app.py) else (echo [FAIL] dashboard\app.py missing)

echo.
echo To start dashboard run: run-dashboard.bat
echo Or: "%PY%" launch_dashboard.py

:end
echo.
pause
