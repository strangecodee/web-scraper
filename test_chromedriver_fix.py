#!/usr/bin/env python3
"""
Test script to verify ChromeDriver compatibility fixes.
"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def test_enhanced_driver_handling():
    """Test the enhanced ChromeDriver handling from the main scripts."""
    print("=" * 60)
    print("TESTING ENHANCED CHROMEDRIVER HANDLING")
    print("=" * 60)
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Test the enhanced get_driver logic
    try:
        # First try webdriver_manager
        driver_path = ChromeDriverManager().install()
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        print("✓ webdriver_manager method: SUCCESS")
        driver.quit()
        return True
    except Exception as e:
        print(f"✗ webdriver_manager method failed: {e}")
        print("Trying fallback methods...")
    
    # Fallback 1: Check for local chromedriver
    local_paths = ['chromedriver.exe', 'chromedriver']
    for path in local_paths:
        if os.path.exists(path):
            try:
                service = Service(path)
                driver = webdriver.Chrome(service=service, options=options)
                print(f"✓ Local ChromeDriver ({path}): SUCCESS")
                driver.quit()
                return True
            except Exception as e:
                print(f"✗ Local ChromeDriver ({path}) failed: {e}")
    
    # Fallback 2: Try system PATH
    try:
        driver = webdriver.Chrome(options=options)
        print("✓ System PATH ChromeDriver: SUCCESS")
        driver.quit()
        return True
    except Exception as e:
        print(f"✗ System PATH ChromeDriver failed: {e}")
    
    print("All ChromeDriver methods failed. Manual installation required.")
    print("Please download ChromeDriver from: https://chromedriver.chromium.org/")
    return False

def main():
    success = test_enhanced_driver_handling()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ ChromeDriver compatibility fix: SUCCESS")
        print("The enhanced driver handling is working correctly!")
    else:
        print("⚠ ChromeDriver compatibility fix: MANUAL INTERVENTION NEEDED")
        print("Please follow the manual installation instructions")
    print("=" * 60)

if __name__ == "__main__":
    main()
