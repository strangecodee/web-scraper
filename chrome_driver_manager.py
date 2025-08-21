#!/usr/bin/env python3
"""
Enhanced ChromeDriver Manager with robust fallback mechanisms.
Handles ChromeDriver compatibility issues and provides multiple solutions.
"""

import os
import sys
import logging
import subprocess
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class EnhancedChromeDriverManager:
    def __init__(self):
        self.chrome_version = self.get_chrome_version()
        self.driver_path = None
        
    def get_chrome_version(self):
        """Get the installed Chrome version."""
        try:
            if sys.platform == "win32":
                # Try to get Chrome version on Windows
                chrome_paths = [
                    os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 
                                'Google\\Chrome\\Application\\chrome.exe'),
                    os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 
                                'Google\\Chrome\\Application\\chrome.exe'),
                ]
                
                for path in chrome_paths:
                    if os.path.exists(path):
                        result = subprocess.run(
                            [path, '--version'],
                            capture_output=True, text=True, timeout=10
                        )
                        if result.returncode == 0:
                            version_line = result.stdout.strip()
                            # Extract version number (e.g., "Google Chrome 139.0.7258.128")
                            if 'Google Chrome' in version_line:
                                return version_line.split('Google Chrome ')[1].split()[0]
            else:
                # For Linux/Mac
                result = subprocess.run(
                    ['google-chrome', '--version'],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    version_line = result.stdout.strip()
                    if 'Google Chrome' in version_line:
                        return version_line.split('Google Chrome ')[1].split()[0]
                        
        except Exception as e:
            logging.warning(f"Could not determine Chrome version: {e}")
            
        return "unknown"
    
    def try_webdriver_manager(self):
        """Try to use webdriver_manager to get ChromeDriver."""
        try:
            logging.info("Attempting to use webdriver_manager...")
            driver_path = ChromeDriverManager().install()
            logging.info(f"✓ ChromeDriver found via webdriver_manager: {driver_path}")
            return driver_path
        except Exception as e:
            logging.warning(f"webdriver_manager failed: {e}")
            return None
    
    def try_compatible_version(self):
        """Try to find a compatible ChromeDriver version."""
        try:
            # Get major version for compatibility
            major_version = self.chrome_version.split('.')[0]
            
            # Try to get the latest available version for this major version
            latest_release_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
            response = requests.get(latest_release_url, timeout=10)
            
            if response.status_code == 200:
                compatible_version = response.text.strip()
                logging.info(f"Found compatible ChromeDriver version: {compatible_version}")
                
                # Try to install this specific version
                driver_path = ChromeDriverManager(version=compatible_version).install()
                logging.info(f"✓ ChromeDriver installed: {driver_path}")
                return driver_path
                
        except Exception as e:
            logging.warning(f"Could not find compatible version: {e}")
            
        return None
    
    def check_local_driver(self):
        """Check if chromedriver.exe exists locally."""
        local_paths = [
            'chromedriver.exe',  # Windows
            'chromedriver',      # Linux/Mac
            os.path.join(os.path.dirname(__file__), 'chromedriver.exe'),
            os.path.join(os.path.dirname(__file__), 'chromedriver')
        ]
        
        for path in local_paths:
            if os.path.exists(path):
                logging.info(f"✓ Found local ChromeDriver: {path}")
                return os.path.abspath(path)
                
        return None
    
    def download_chromedriver_manual(self):
        """Provide instructions for manual download."""
        major_version = self.chrome_version.split('.')[0]
        download_url = f"https://chromedriver.chromium.org/downloads"
        
        print("\n" + "="*60)
        print("MANUAL CHROMEDRIVER INSTALLATION REQUIRED")
        print("="*60)
        print(f"Your Chrome version: {self.chrome_version}")
        print(f"Recommended ChromeDriver version: {major_version}.x.x")
        print()
        print("Steps to fix:")
        print("1. Visit: https://chromedriver.chromium.org/downloads")
        print("2. Download ChromeDriver for your platform")
        print("3. Extract the chromedriver executable")
        print("4. Place it in this project folder")
        print("5. The scraper will automatically detect it")
        print()
        print("Alternative: Use Chrome version 138 or earlier")
        print("="*60)
        
        return None
    
    def get_driver_path(self):
        """Get ChromeDriver path using multiple fallback strategies."""
        logging.info(f"Chrome version detected: {self.chrome_version}")
        
        # Strategy 1: Check for local chromedriver
        local_driver = self.check_local_driver()
        if local_driver:
            return local_driver
        
        # Strategy 2: Try webdriver_manager
        driver_path = self.try_webdriver_manager()
        if driver_path:
            return driver_path
        
        # Strategy 3: Try compatible version
        driver_path = self.try_compatible_version()
        if driver_path:
            return driver_path
        
        # Strategy 4: Manual download instructions
        return self.download_chromedriver_manual()
    
    def test_driver(self, driver_path):
        """Test if the ChromeDriver works."""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            
            driver.get('https://httpbin.org/html')
            title = driver.title
            driver.quit()
            
            logging.info(f"✓ ChromeDriver test successful: {title}")
            return True
            
        except Exception as e:
            logging.error(f"ChromeDriver test failed: {e}")
            return False

def main():
    """Main function to test ChromeDriver setup."""
    print("="*60)
    print("ENHANCED CHROMEDRIVER MANAGER")
    print("="*60)
    
    manager = EnhancedChromeDriverManager()
    driver_path = manager.get_driver_path()
    
    if driver_path and os.path.exists(driver_path):
        print(f"✓ ChromeDriver found: {driver_path}")
        
        # Test the driver
        if manager.test_driver(driver_path):
            print("✓ ChromeDriver is working correctly!")
            print("\nYou can now run the scraping scripts:")
            print("- python enhanced_scrape_dues.py")
            print("- python daily_scraper.py")
        else:
            print("⚠ ChromeDriver found but not working properly")
            print("Please check the ChromeDriver version compatibility")
    else:
        print("⚠ ChromeDriver not found")
        print("Please follow the manual installation instructions above")
    
    print("="*60)

if __name__ == "__main__":
    main()
