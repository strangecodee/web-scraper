#!/usr/bin/env python3
"""
Setup script for the web scraping project.
This script will install required dependencies and provide instructions.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install the required packages from requirements.txt"""
    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install packages: {e}")
        return False

def check_chrome_installed():
    """Check if Chrome browser is installed"""
    try:
        # Try to find Chrome on Windows
        if sys.platform == "win32":
            chrome_paths = [
                os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Google\\Chrome\\Application\\chrome.exe'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'Google\\Chrome\\Application\\chrome.exe'),
            ]
            for path in chrome_paths:
                if os.path.exists(path):
                    print("✓ Chrome browser found")
                    return True
        else:
            # For Linux/Mac, try which command
            result = subprocess.run(['which', 'google-chrome'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Chrome browser found")
                return True
        
        print("⚠ Chrome browser not found. Please install Chrome for Selenium to work properly.")
        return False
    except Exception as e:
        print(f"⚠ Could not check Chrome installation: {e}")
        return True  # Assume it's installed

def main():
    print("=" * 50)
    print("Web Scraping Project Setup")
    print("=" * 50)
    
    # Check if virtual environment exists
    if not os.path.exists('.venv'):
        print("⚠ No virtual environment found. It's recommended to use a virtual environment.")
        print("   You can create one with: python -m venv .venv")
        print("   Then activate it and run this script again.")
        response = input("Continue without virtual environment? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Install requirements
    if install_requirements():
        check_chrome_installed()
        
        print("\n" + "=" * 50)
        print("Setup Complete!")
        print("=" * 50)
        print("\nTo run the project:")
        print("1. Make sure you have an Excel file with 'link' column")
        print("2. Run: python enhanced_scrape_dues.py")
        print("3. Select your Excel file when prompted")
        print("\nAvailable scripts:")
        print("- enhanced_scrape_dues.py: Main scraping script with GUI")
        print("- extract_links.py: Extract links from Excel to text file")
        print("- scrape_dues.py: Basic scraping script")
    else:
        print("\nSetup failed. Please check your Python/pip installation.")

if __name__ == "__main__":
    main()
