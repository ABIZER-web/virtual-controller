@echo off
setlocal
title VIRTUAL DRIVE — Racing Simulator Controller
cd /d "%~dp0"

echo =====================================================================
echo          VIRTUAL DRIVE -- Virtual Racing Simulator Controller
echo =====================================================================
echo.
echo Launching Virtual Drive...
echo (You can minimize this window while racing)
echo.

:: Detect Python executable
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "PY_CMD=python"
    goto check_deps
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "PY_CMD=py"
    goto check_deps
)

echo [ERROR] Python was not found in your system PATH!
echo.
echo Please install Python 3.11+ from https://www.python.org/
echo Make sure to check the box "Add Python to PATH" during installation.
echo.
pause
exit /b 1

:check_deps
:: Verify critical dependencies and launch application
%PY_CMD% -c "import cv2, mediapipe, PySide6, vgamepad" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing required libraries from requirements.txt...
    %PY_CMD% -m pip install -r requirements.txt
    echo.
)

:: Run main application
%PY_CMD% main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [NOTICE] Application closed with code %ERRORLEVEL%.
    pause
)

exit /b 0
