@echo off
REM Re-launch in a visible window that stays open when double-clicked from Explorer.
if /i not "%~1"=="INTERNAL" (
  start "PPAP Dashboard" cmd /k ""%~f0" INTERNAL"
  exit /b
)

setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
set "LOG=%~dp0dashboard-launch.log"

echo [%date% %time%] Dashboard launch started > "%LOG%"
echo.
echo  PPAP Level 3 Streamlit Dashboard
echo  ================================
echo  Log file: %LOG%
echo.

REM --- Find Python ---
set "PY="
where py >nul 2>&1 && set "PY=py"
if not defined PY where python >nul 2>&1 && set "PY=python"

if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
  set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
)
if not defined PY if exist "C:\Program Files\Python313\python.exe" (
  set "PY=C:\Program Files\Python313\python.exe"
)
if not defined PY if exist "%APPDATA%\Python\Python313\python.exe" (
  set "PY=%APPDATA%\Python\Python313\python.exe"
)

if not defined PY (
  echo ERROR: Python not found. Install from https://www.python.org/downloads/
  echo ERROR: Python not found >> "%LOG%"
  goto :fail
)

echo Using Python: %PY%
echo Using Python: %PY% >> "%LOG%"
"%PY%" --version
"%PY%" --version >> "%LOG%" 2>&1

REM --- Install dependencies (quote specs - unquoted ^>= breaks in CMD) ---
echo.
echo [1/3] Installing streamlit and pypdf...
echo [1/3] Installing dependencies >> "%LOG%"
"%PY%" -m pip install --user --upgrade pip >> "%LOG%" 2>&1
"%PY%" -m pip install --user "streamlit>=1.32" "pypdf>=4.0" >> "%LOG%" 2>&1
if errorlevel 1 (
  echo ERROR: pip install failed. See %LOG%
  goto :fail
)

REM --- Verify streamlit import ---
echo.
echo [2/3] Verifying streamlit...
"%PY%" -c "import streamlit; print('streamlit', streamlit.__version__)" 2>> "%LOG%"
if errorlevel 1 (
  echo ERROR: streamlit is not installed for this Python.
  echo Try: "%PY%" -m pip install --user streamlit
  goto :fail
)

REM --- Open browser after short delay ---
echo.
echo [3/3] Starting dashboard...
echo Browser should open at http://localhost:8501
echo Keep this window open while using the dashboard.
echo.
start "" cmd /c "timeout /t 4 /nobreak >nul && start http://localhost:8501"

"%PY%" -m streamlit run "%~dp0dashboard\app.py" --server.port 8501 --browser.serverAddress localhost --browser.gatherUsageStats false
set "RC=!ERRORLEVEL!"
echo Streamlit exited with code !RC! >> "%LOG%"

if !RC! neq 0 goto :fail
goto :end

:fail
echo.
echo ========================================
echo  Dashboard failed to start.
echo  Open this file for details:
echo  %LOG%
echo ========================================
echo.
pause
exit /b 1

:end
echo.
echo Dashboard stopped.
pause
exit /b 0
