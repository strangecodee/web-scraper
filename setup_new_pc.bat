@echo off
echo ================================================
echo    Optimized Web Scraper - New PC Setup
echo ================================================
echo.
echo This batch file will set up the web scraper on a new PC.
echo It will install all required dependencies and configure
echo the environment for optimal performance.
echo.
echo Requirements:
echo - Python 3.7+ installed
echo - Chrome browser installed
echo - Internet connection for downloads
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo Step 1: Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found or not in PATH
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

echo.
echo Step 2: Running automated setup...
python setup_optimized_scraper.py

echo.
echo Step 3: Creating desktop shortcut (Windows only)...
echo [InternetShortcut] > "%USERPROFILE%\Desktop\Web Scraper Setup.url"
echo URL=file:///%CD% >> "%USERPROFILE%\Desktop\Web Scraper Setup.url"
echo IconIndex=0 >> "%USERPROFILE%\Desktop\Web Scraper Setup.url"
echo IconFile=%CD%\setup.ico >> "%USERPROFILE%\Desktop\Web Scraper Setup.url"

echo.
echo ================================================
echo    SETUP COMPLETE!
echo ================================================
echo.
echo Next steps:
echo 1. Edit links.txt with your target URLs
echo 2. Run the scraper: double-click run_optimized.bat
echo 3. Or run manually: python portable_optimized_scraper.py
echo.
echo Files created:
echo - links.txt (add your URLs here)
echo - run_optimized.bat (double-click to run)
echo - QUICK_START.md (setup instructions)
echo - Desktop shortcut for easy access
echo.
echo Press any key to exit...
pause >nul
