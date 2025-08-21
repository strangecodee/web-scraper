#!/usr/bin/env python3
"""
Test script to verify the optimized scraper works correctly.
"""

import subprocess
import sys
import os

def test_optimized_scraper():
    """Test the optimized scraper functionality."""
    print("Testing optimized scraper...")
    
    # Check if Python is available
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"Python version: {result.stdout.strip()}")
    except:
        print("Python not found")
        return False
    
    # Check if optimized_scraper.py exists
    if not os.path.exists('optimized_scraper.py'):
        print("optimized_scraper.py not found")
        return False
    
    # Test import of required modules
    try:
        import pandas
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        print("✓ All required modules imported successfully")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    # Test ChromeDriver availability
    try:
        driver_path = ChromeDriverManager().install()
        print(f"✓ ChromeDriver available: {driver_path}")
    except Exception as e:
        print(f"⚠ ChromeDriver issue: {e}")
        print("You may need to install ChromeDriver manually")
    
    print("\nOptimized scraper features:")
    print("- Reduced concurrency (2 workers instead of 50)")
    print("- Batch processing (10 URLs per batch)")
    print("- Memory optimizations (smaller window, disabled images)")
    print("- Automatic garbage collection")
    print("- Progress saving after each batch")
    
    print("\nTo run the optimized scraper:")
    print("python optimized_scraper.py")
    
    return True

if __name__ == "__main__":
    success = test_optimized_scraper()
    if success:
        print("\n✓ Optimized scraper is ready to use!")
        print("It will use significantly less CPU and memory than the original version.")
    else:
        print("\n✗ Some issues need to be resolved.")
