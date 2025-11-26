@echo off
echo ========================================
echo    ForensiQ (Network) - Starting...
echo ========================================
echo.

python run_gui.py

if errorlevel 1 (
    echo.
    echo Error starting application!
    echo Make sure Python is installed and dependencies are available.
    pause
)

