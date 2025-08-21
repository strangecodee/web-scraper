#!/usr/bin/env python3
"""
Test script to verify the portable optimized scraper works correctly.
This tests the basic functionality without actually scraping websites.
"""

import os
import sys
import tempfile
import pandas as pd
from portable_optimized_scraper import PortableOptimizedScraper

def test_setup():
    """Test that the scraper can be initialized properly."""
    print("🧪 Testing scraper initialization...")
    try:
        scraper = PortableOptimizedScraper(headless=True)
        print("✅ Scraper initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Scraper initialization failed: {e}")
        return False

def test_directories():
    """Test that required directories are created."""
    print("🧪 Testing directory creation...")
    try:
        scraper = PortableOptimizedScraper(headless=True)
        
        # Check if directories exist
        directories = ['screenshots', 'logs', 'data']
        for directory in directories:
            if os.path.exists(directory):
                print(f"✅ Directory '{directory}' exists")
            else:
                print(f"❌ Directory '{directory}' missing")
                return False
                
        return True
    except Exception as e:
        print(f"❌ Directory test failed: {e}")
        return False

def test_excel_creation():
    """Test Excel file creation functionality."""
    print("🧪 Testing Excel file creation...")
    try:
        # Create test links file
        test_links = [
            "https://example.com/page1",
            "https://example.com/page2", 
            "https://example.com/page3"
        ]
        
        with open('test_links.txt', 'w') as f:
            for link in test_links:
                f.write(f"{link}\n")
        
        # Test the method that creates Excel files
        scraper = PortableOptimizedScraper(headless=True)
        
        # Test creating Excel from links
        df = scraper.process_links_optimized(input_file='test_links.txt', excel_file=None, max_workers=1)
        
        if df is not None and len(df) == 3:
            print("✅ Excel file creation test passed")
            
            # Clean up test file
            if os.path.exists('test_links.txt'):
                os.remove('test_links.txt')
            if os.path.exists('data/scraping_results.xlsx'):
                os.remove('data/scraping_results.xlsx')
                
            return True
        else:
            print("❌ Excel file creation test failed")
            return False
            
    except Exception as e:
        print(f"❌ Excel test failed: {e}")
        # Clean up on error
        if os.path.exists('test_links.txt'):
            os.remove('test_links.txt')
        return False

def test_dependencies():
    """Test that all required dependencies are available."""
    print("🧪 Testing dependencies...")
    
    dependencies = [
        ('selenium', '4.1.3'),
        ('pandas', '1.3.5'),
        ('webdriver_manager', '4.0.1'),
        ('openpyxl', '3.1.2')
    ]
    
    all_ok = True
    
    for package, expected_version in dependencies:
        try:
            module = __import__(package)
            actual_version = getattr(module, '__version__', 'unknown')
            
            if actual_version.startswith(expected_version):
                print(f"✅ {package}=={actual_version} (expected: {expected_version})")
            else:
                print(f"⚠️  {package}=={actual_version} (expected: {expected_version})")
                all_ok = False
                
        except ImportError:
            print(f"❌ {package} not installed")
            all_ok = False
    
    return all_ok

def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 PORTABLE OPTIMIZED SCRAPER TEST SUITE")
    print("=" * 60)
    print("Running comprehensive tests...")
    print()
    
    tests = [
        ("Dependency Check", test_dependencies),
        ("Scraper Initialization", test_setup),
        ("Directory Creation", test_directories),
        ("Excel File Creation", test_excel_creation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\n📈 Score: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The portable scraper is ready to use.")
        print("\nNext steps:")
        print("1. Add your URLs to links.txt")
        print("2. Run: python portable_optimized_scraper.py")
        print("3. Or use: python setup_optimized_scraper.py for fresh setup")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the setup.")
        print("Run: python setup_optimized_scraper.py to fix dependencies")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
