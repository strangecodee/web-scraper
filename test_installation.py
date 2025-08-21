#!/usr/bin/env python3
"""
Test script to verify that all dependencies are installed correctly.
"""

import importlib
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

def main():
    print("Testing Python installation...")
    print(f"Python version: {sys.version}")
    print()
    
    print("Testing required modules:")
    modules_to_test = [
        'selenium',
        'pandas',
        'webdriver_manager',
        'openpyxl',
        'tkinter',
        'concurrent.futures',
        'logging',
        'os'
    ]
    
    all_passed = True
    for module in modules_to_test:
        if not test_import(module):
            all_passed = False
    
    print()
    if all_passed:
        print("✓ All tests passed! Your environment is ready for web scraping.")
        print("\nYou can now run:")
        print("  python enhanced_scrape_dues.py")
    else:
        print("✗ Some tests failed. Please check your installation.")
        print("Try running: python setup.py")

if __name__ == "__main__":
    main()
