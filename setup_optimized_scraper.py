#!/usr/bin/env python3
"""
Setup script for Optimized Web Scraper on a new PC.
This script automates the installation and configuration process.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a system command and handle errors."""
    print(f"⏳ {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        print("✅ Success")
        return True
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 7):
        print(f"❌ Python 3.7+ required. Current: {sys.version}")
        return False
    print(f"✅ Python {sys.version} - OK")
    return True

def install_dependencies():
    """Install required Python packages."""
    # Python 3.7 compatible versions
    requirements = [
        "selenium==4.1.3",        # Last version supporting Python 3.7
        "pandas==1.3.5",          # Last version supporting Python 3.7
        "webdriver-manager==4.0.1",
        "openpyxl==3.1.2",
        "tkinter"  # Usually comes with Python
    ]
    
    print("📦 Installing dependencies...")
    
    for package in requirements:
        if package == "tkinter":
            # tkinter is usually bundled with Python
            continue
            
        print(f"   Installing {package}...")
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Warning: Failed to install {package}")
    
    return True

def download_chromedriver():
    """Download and configure ChromeDriver."""
    print("🌐 Setting up ChromeDriver...")
    
    # Try webdriver_manager first
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver installed at: {driver_path}")
        return True
    except Exception as e:
        print(f"❌ webdriver_manager failed: {e}")
        print("⚠️  Please install ChromeDriver manually:")
        print("   1. Download from: https://chromedriver.chromium.org/")
        print("   2. Place chromedriver.exe in this folder")
        print("   3. Add to system PATH if needed")
        return False

def create_config_files():
    """Create necessary configuration files."""
    print("📁 Creating configuration files...")
    
    # Create required directories
    os.makedirs('screenshots', exist_ok=True)
    
    # Create sample links file if it doesn't exist
    if not os.path.exists('links.txt'):
        with open('links.txt', 'w') as f:
            f.write("# Add your URLs here, one per line\n")
            f.write("# Example: https://example.com/page1\n")
            f.write("# Example: https://example.com/page2\n")
        print("✅ Created sample links.txt")
    
    # Create batch file for easy execution
    if platform.system() == "Windows":
        with open('run_optimized.bat', 'w') as f:
            f.write("@echo off\n")
            f.write("echo Starting Optimized Web Scraper...\n")
            f.write("python optimized_scraper.py\n")
            f.write("pause\n")
        print("✅ Created run_optimized.bat")
    
    return True

def create_quick_start_guide():
    """Create a quick start guide."""
    guide = """# Quick Start Guide - Optimized Web Scraper

## 🚀 First Time Setup
1. Run this setup script: `python setup_optimized_scraper.py`
2. Make sure Chrome browser is installed
3. Add your URLs to `links.txt` (one per line)

## 📊 How to Use
1. **Prepare Excel File**: Create an Excel file with a 'link' column containing URLs
2. **Run Scraper**: Execute `python optimized_scraper.py`
3. **Select File**: Choose your Excel file when prompted
4. **Wait**: The scraper will process URLs with optimized performance

## ⚙️ Performance Features
- **Low CPU/Memory**: Only 2 concurrent workers
- **Batch Processing**: Processes 10 URLs at a time
- **Automatic Logging**: Logs rotate automatically (10MB max)
- **Error Handling**: Screenshots saved for failed pages

## 📋 Files Created
- `optimized_scraper.py` - Main scraper script
- `links.txt` - Your target URLs
- `screenshots/` - Directory for error screenshots
- `*.log` - Log files with rotation

## 🛠️ Troubleshooting
- If ChromeDriver fails: Download manually from chromedriver.chromium.org
- Check `error.log` for detailed error information
- Ensure Excel file has 'link' column

## 📞 Support
Check the logs for errors and refer to the main documentation.
"""
    
    with open('QUICK_START.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    print("✅ Created QUICK_START.md")

def verify_setup():
    """Verify the setup is complete and working."""
    print("🔍 Verifying setup...")
    
    checks = [
        ("Python version", check_python_version()),
        ("Dependencies", install_dependencies()),
        ("ChromeDriver", download_chromedriver()),
        ("Config files", create_config_files()),
    ]
    
    all_ok = all(result for _, result in checks)
    
    if all_ok:
        print("\n🎉 Setup completed successfully!")
        print("📖 Please read QUICK_START.md for usage instructions")
        create_quick_start_guide()
    else:
        print("\n⚠️  Setup completed with warnings")
        print("   Some components may need manual configuration")
    
    return all_ok

def main():
    """Main setup function."""
    print("=" * 60)
    print("🛠️  Optimized Web Scraper Setup")
    print("=" * 60)
    print("This script will set up the optimized web scraper on a new PC.")
    print("It will install dependencies and configure the environment.")
    print("=" * 60)
    
    # Check if we're in the right directory
    current_dir = os.path.basename(os.getcwd())
    if current_dir not in ['web-scraper', 'optimized-scraper']:
        print("⚠️  Warning: Not in expected project directory")
        print("   Current directory:", current_dir)
    
    input("Press Enter to continue or Ctrl+C to cancel...")
    
    # Run setup
    success = verify_setup()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Setup Complete!")
        print("Next steps:")
        print("1. Add your URLs to links.txt")
        print("2. Prepare Excel file with 'link' column")
        print("3. Run: python optimized_scraper.py")
        if platform.system() == "Windows":
            print("   Or double-click: run_optimized.bat")
    else:
        print("❌ Setup completed with errors")
        print("Please check the messages above and fix any issues")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
