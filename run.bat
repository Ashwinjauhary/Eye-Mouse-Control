@echo off
echo Eye Mouse Control - Quick Start
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
pip show opencv-python >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Show menu
echo.
echo Choose an option:
echo 1. Run Eye Mouse Control
echo 2. Open Configuration GUI
echo 3. Run System Tests
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo Starting Eye Mouse Control...
    echo Press ESC to exit, SPACE to pause/resume, C to calibrate
    python eye_mouse_control.py
) else if "%choice%"=="2" (
    echo Opening Configuration GUI...
    python config_gui.py
) else if "%choice%"=="3" (
    echo Running system tests...
    python test_system.py
) else if "%choice%"=="4" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice
    pause
)

echo.
pause
