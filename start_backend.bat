@echo off
echo HFCL Cable Data Processing Backend
echo ===================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo Choose an option:
echo 1. Start Backend (Normal)
echo 2. Cleanup Files (Fix permission issues)
echo 3. Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto start_backend
if "%choice%"=="2" goto cleanup_files
if "%choice%"=="3" goto exit
echo Invalid choice. Please try again.
pause
goto :eof

:cleanup_files
echo.
echo Starting file cleanup...
cd backend
python cleanup_files.py
cd ..
echo.
echo Cleanup complete! You can now start the backend.
pause
goto :eof

:start_backend
echo.
echo Starting HFCL Cable Data Processing Backend...
echo.

REM Navigate to backend directory
cd backend

REM Install dependencies if requirements.txt exists
if exist requirements.txt (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo WARNING: Failed to install some dependencies
        echo Continuing anyway...
    )
    echo.
)

REM Start the backend using the simple startup method
echo Starting Flask backend (Windows-compatible mode)...
python run_simple.py

:exit
pause
