@echo off
echo ============================================
echo   Pixel Master - Build Script
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.11+ from python.org
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo [2/3] Cleaning previous build...
if exist "dist\PixelMaster.exe" del /f /q "dist\PixelMaster.exe"
if exist "build" rmdir /s /q build

echo [3/3] Building PixelMaster.exe...
pyinstaller pixelrevive.spec --noconfirm

if exist "dist\PixelMaster.exe" (
    echo.
    echo ============================================
    echo   Build complete!
    echo   Output: dist\PixelMaster.exe
    echo ============================================
    explorer dist
) else (
    echo.
    echo [ERROR] Build failed. Check output above.
)

pause
