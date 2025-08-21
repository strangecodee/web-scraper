#!/usr/bin/env python3
"""
Test script to verify daily scraping setup is working correctly.
"""

import importlib
import os
import sys

def test_import(module_name):
    """Test if a module can be imported successfully."""
    try:
        importlib.import_module(module_name)
        print(f"✓ {module_name}: OK")
        return True
    except ImportError as e:
        print(f"✗ {module_name}: FAILED - {e}")
        return False

def test_directory_structure():
    """Test if required directories exist."""
    required_dirs = ['screenshots', 'archive']
    all_ok = True
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✓ Directory {dir_name}/: EXISTS")
        else:
            print(f"⚠ Directory {dir_name}/: MISSING (will be created automatically)")
            all_ok = False
    
    return all_ok

def test_files_exist():
    """Test if required files exist."""
    required_files = [
        'daily_scraper.py',
        'schedule_scraper.py', 
        'requirements.txt',
        'DAILY_SCRAPING_GUIDE.md'
    ]
    
    all_ok = True
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"✓ File {file_name}: EXISTS")
        else:
            print(f"✗ File {file_name}: MISSING")
            all_ok = False
    
    return all_ok

def main():
    print("=" * 60)
    print("DAILY SCRAPING SETUP VERIFICATION")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print()
    
    print("1. Testing module imports:")
    print("-" * 30)
    
    modules_to_test = [
        'selenium',
        'pandas', 
        'webdriver_manager',
        'openpyxl',
        'schedule',
        'tkinter',
        'concurrent.futures',
        'logging',
        'os'
    ]
    
    all_imports_ok = True
    for module in modules_to_test:
        if not test_import(module):
            all_imports_ok = False
    
    print()
    print("2. Testing directory structure:")
    print("-" * 30)
    dirs_ok = test_directory_structure()
    
    print()
    print("3. Testing required files:")
    print("-" * 30)
    files_ok = test_files_exist()
    
    print()
    print("4. Summary:")
    print("-" * 30)
    
    if all_imports_ok and dirs_ok and files_ok:
        print("✓ ALL TESTS PASSED!")
        print("\nYour daily scraping setup is ready!")
        print("\nNext steps:")
        print("1. Run: python daily_scraper.py (for manual daily run)")
        print("2. Run: python schedule_scraper.py (for automated scheduling)")
        print("3. Read: DAILY_SCRAPING_GUIDE.md (for complete instructions)")
    else:
        print("⚠ SOME TESTS FAILED")
        print("\nPlease check the issues above.")
        
        if not all_imports_ok:
            print("- Run: pip install -r requirements.txt")
        if not files_ok:
            print("- Missing required files")
        if not dirs_ok:
            print("- Directories will be created automatically during first run")

if __name__ == "__main__":
    main()
