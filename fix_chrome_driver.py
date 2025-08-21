#!/usr/bin/env python3
"""
Enhanced ChromeDriver compatibility fixer.
This script provides multiple solutions for Chrome driver version mismatches.
"""

import os
import subprocess
import sys
import requests
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_chrome_version():
    """Check the installed Chrome version with multiple fallback methods."""
    try:
        # Method 1: Try registry on Windows
        if sys.platform == "win32":
            try:
                import winreg
                # Try to read Chrome version from registry
                key_path = r"SOFTWARE\Google\Chrome\BLBeacon"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                    version, _ = winreg.QueryValueEx(key, "version")
                    if version:
                        return version
            except:
                pass
        
        # Method 2: Try executable path with shorter timeout
        if sys.platform == "win32":
            chrome_paths = [
                os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 
                            'Google\\Chrome\\Application\\chrome.exe'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 
                            'Google\\Chrome\\Application\\chrome.exe'),
                os.path.join(os.environ.get('LOCALAPPDATA', 'C:\\Users\\%USERNAME%\\AppData\\Local'), 
                            'Google\\Chrome\\Application\\chrome.exe'),
            ]
            
            for path in chrome_paths:
                if os.path.exists(path):
                    try:
                        result = subprocess.run(
                            [path, '--version'],
                            capture_output=True, text=True, timeout=5
                        )
                        if result.returncode == 0:
                            version_line = result.stdout.strip()
                            if 'Google Chrome' in version_line:
                                return version_line.split('Google Chrome ')[1].split()[0]
                    except:
                        continue
        
        # Method 3: Try system command with shorter timeout
        try:
            if sys.platform == "win32":
                result = subprocess.run(
                    ['wmic', 'datafile', 'where', 'name="C:\\\\Program Files\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe"', 'get', 'Version'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        version = lines[1].strip()
                        if version:
                            return version
            else:
                result = subprocess.run(
                    ['google-chrome', '--version'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    version_line = result.stdout.strip()
                    if 'Google Chrome' in version_line:
                        return version_line.split('Google Chrome ')[1].split()[0]
        except:
            pass
            
    except Exception as e:
        logging.warning(f"Could not determine Chrome version: {e}")
    
    # Fallback: Try to get version from common installation paths
    try:
        if sys.platform == "win32":
            # Check common installation directories for version file
            install_dirs = [
                os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Google\\Chrome\\Application'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'Google\\Chrome\\Application'),
                os.path.join(os.environ.get('LOCALAPPDATA', 'C:\\Users\\%USERNAME%\\AppData\\Local'), 'Google\\Chrome\\Application'),
            ]
            
            for install_dir in install_dirs:
                if os.path.exists(install_dir):
                    # Look for version files or directories
                    for item in os.listdir(install_dir):
                        if item.replace('.', '').isdigit() and len(item.split('.')) == 4:
                            return item
    except:
        pass
        
    return "unknown"

def check_local_chromedriver():
    """Check if chromedriver.exe exists locally."""
    local_paths = [
        'chromedriver.exe',  # Windows
        'chromedriver',      # Linux/Mac
        os.path.join(os.path.dirname(__file__), 'chromedriver.exe'),
        os.path.join(os.path.dirname(__file__), 'chromedriver')
    ]
    
    for path in local_paths:
        if os.path.exists(path):
            logging.info(f"Found local ChromeDriver: {path}")
            return os.path.abspath(path)
            
    return None

def test_chromedriver(driver_path=None):
    """Test if ChromeDriver is working."""
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        if driver_path:
            service = Service(driver_path)
        else:
            # Try webdriver_manager
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get('https://httpbin.org/html')
        title = driver.title
        driver.quit()
        
        logging.info(f"✓ ChromeDriver test successful: {title}")
        return True
        
    except Exception as e:
        logging.error(f"✗ ChromeDriver test failed: {e}")
        return False

def get_compatible_version(chrome_version):
    """Try to find a compatible ChromeDriver version."""
    try:
        # Get major version for compatibility
        major_version = chrome_version.split('.')[0]
        
        # Try to get the latest available version for this major version
        latest_release_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
        response = requests.get(latest_release_url, timeout=10)
        
        if response.status_code == 200:
            compatible_version = response.text.strip()
            logging.info(f"Found compatible ChromeDriver version: {compatible_version}")
            return compatible_version
            
    except Exception as e:
        logging.warning(f"Could not find compatible version: {e}")
        
    return None

def download_chromedriver_instructions(chrome_version):
    """Provide instructions for manual download."""
    major_version = chrome_version.split('.')[0]
    
    print("\n" + "=" * 60)
    print("MANUAL CHROMEDRIVER INSTALLATION REQUIRED")
    print("=" * 60)
    print(f"Your Chrome version: {chrome_version}")
    print(f"Recommended ChromeDriver version: {major_version}.x.x")
    print()
    print("Steps to fix:")
    print("1. Visit: https://chromedriver.chromium.org/downloads")
    print("2. Download ChromeDriver for your platform (Windows/Linux/Mac)")
    print("3. Extract the chromedriver executable")
    print("4. Place it in this project folder")
    print("5. The scraper will automatically detect it")
    print()
    print("Alternative solutions:")
    print("- Use Chrome version 138 or earlier")
    print("- Wait for ChromeDriver 139.x.x to be released")
    print("- Use the chrome_driver_manager.py script for automated solutions")
    print("=" * 60)

def fix_chrome_driver():
    """Main function to fix ChromeDriver issues with enhanced capabilities."""
    print("=" * 60)
    print("ENHANCED CHROMEDRIVER FIXER")
    print("=" * 60)
    
    chrome_version = check_chrome_version()
    print(f"Chrome version detected: {chrome_version}")
    
    if chrome_version == "unknown":
        print("⚠ Could not detect Chrome version. Please ensure Chrome is installed.")
        return False
    
    # Check for local chromedriver first
    local_driver = check_local_chromedriver()
    if local_driver:
        print(f"✓ Found local ChromeDriver: {local_driver}")
        print("Testing local ChromeDriver...")
        if test_chromedriver(local_driver):
            print("✓ Local ChromeDriver is working correctly!")
            return True
        else:
            print("⚠ Local ChromeDriver found but not working")
    
    print("\nTesting ChromeDriver via webdriver_manager...")
    if test_chromedriver():
        print("✓ ChromeDriver is working correctly via webdriver_manager!")
        return True
    
    print("\n" + "=" * 60)
    print("CHROMEDRIVER COMPATIBILITY ISSUE DETECTED")
    print("=" * 60)
    
    # Try to find compatible version
    compatible_version = get_compatible_version(chrome_version)
    if compatible_version:
        print(f"Found compatible version: {compatible_version}")
        print("Attempting to install compatible version...")
        try:
            driver_path = ChromeDriverManager(version=compatible_version).install()
            if test_chromedriver(driver_path):
                print(f"✓ Compatible ChromeDriver {compatible_version} installed and working!")
                return True
        except Exception as e:
            print(f"Failed to install compatible version: {e}")
    
    # Provide manual download instructions
    download_chromedriver_instructions(chrome_version)
    
    print("\nAdditional solutions available:")
    print("- Run: python chrome_driver_manager.py (for automated solutions)")
    print("- Check the README.md for troubleshooting guide")
    
    return False

def main():
    success = fix_chrome_driver()
    
    print()
    print("=" * 60)
    if success:
        print("✓ Chrome driver issue resolved!")
        print("You can now run: python daily_scraper.py")
        print("Or: python enhanced_scrape_dues.py")
    else:
        print("⚠ Manual intervention required")
        print("Please follow the instructions above to download ChromeDriver manually")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
