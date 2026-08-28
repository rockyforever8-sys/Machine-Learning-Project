@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo  PPAP Level 3 Streamlit Dashboard
echo  ================================
echo.

REM Prefer Windows Python launcher, then python on PATH
where py >nul 2>&1
if %ERRORLEVEL%==0 (
  set "PY=py"
) else (
  set "PY=python"
)

echo Using: %PY%
echo.

echo [1/2] Installing streamlit and pypdf...
%PY% -m pip install --user --upgrade pip
%PY% -m pip install --user streamlit>=1.32 pypdf>=4.0
if %ERRORLEVEL% neq 0 (
  echo.
  echo ERROR: Could not install dependencies.
  echo Try running this file as Administrator, or install Python from python.org
  echo.
  pause
  exit /b 1
)

echo.
echo [2/2] Starting dashboard in your browser...
echo Close this window to stop the dashboard.
echo.

%PY% -m streamlit run dashboard\app.py
if %ERRORLEVEL% neq 0 (
  echo.
  echo ERROR: Could not start Streamlit.
  echo Run manually: %PY% -m pip install --user streamlit
  echo Then:         %PY% -m streamlit run dashboard\app.py
  echo.
)

pause
