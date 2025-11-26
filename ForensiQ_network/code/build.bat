@echo off
echo ========================================
echo    ForensiQ (Network) Build Script
echo ========================================
echo.

python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo Building ForensiQ (Network) GUI executable...
echo This may take several minutes...
echo.

python build_exe.py

if errorlevel 1 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Build Complete!
echo ========================================
echo.
echo Executable location: dist\ForensiQ.exe
echo.
pause

