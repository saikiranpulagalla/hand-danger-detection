@echo off
REM Quick start launcher for Hand Danger Detection System

echo.
echo ============================================================
echo  Hand Danger Detection System - Launcher
echo ============================================================
echo.
echo Choose mode:
echo  1. Demo Mode (Simulated Hand - Works Now!)
echo  2. Real Mode (Requires Webcam)
echo  3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Starting Demo Mode...
    python main_demo.py
) else if "%choice%"=="2" (
    echo.
    echo Starting Real Mode...
    python main.py
) else (
    echo Exiting...
)

pause
