#!/usr/bin/env python3
"""
Fix for Chrome driver compatibility issues.
This script helps resolve Chrome driver version mismatches.
"""

import os
import subprocess
import sys

def fix_chrome_driver():
    """Fix Chrome driver compatibility issues."""
    print("=" * 50)
    print("CHROME DRIVER COMPATIBILITY FIX")
    print("=" * 50)
    
    print("Your Chrome version: 139.0.7258.128")
    print("Issue: webdriver_manager cannot find matching driver")
    print()
    
    print("Solution 1: Manual driver download")
    print("- Download ChromeDriver from: https://chromedriver.chromium.org/")
    print("- Look for version 139.0.7258.x")
    print("- Extract chromedriver.exe to this folder")
    print()
    
    print("Solution 2: Use different webdriver manager approach")
    print("Trying alternative approach...")
    
    try:
        # Try to clear webdriver manager cache and retry
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        # Clear cache first
        print("Clearing webdriver manager cache...")
        chrome_driver_path = ChromeDriverManager().install()
        print(f"Chrome driver path: {chrome_driver_path}")
        
        # Test with the driver
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get('https://httpbin.org/html')
        print(f"✓ Success! Page title: {driver.title}")
        driver.quit()
        
        return True
        
    except Exception as e:
        print(f"Alternative approach failed: {e}")
        print()
        print("RECOMMENDED: Manual driver installation")
        print("1. Visit: https://chromedriver.chromium.org/")
        print("2. Download ChromeDriver 139.0.7258.x")
        print("3. Place chromedriver.exe in this folder")
        print("4. The scraper will use the local driver automatically")
        return False

def main():
    success = fix_chrome_driver()
    
    print()
    print("=" * 50)
    if success:
        print("✓ Chrome driver issue resolved!")
        print("You can now run: python daily_scraper.py")
    else:
        print("⚠ Manual intervention required")
        print("Please download ChromeDriver manually as instructed above")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
