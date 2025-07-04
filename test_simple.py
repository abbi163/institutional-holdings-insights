#!/usr/bin/env python3
"""
Simple test script to verify the basic setup without complex dependencies
"""

import sys
import os

# Add src to path
sys.path.append('src')

def test_imports():
    """Test if all modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import selenium
        print(f"✅ Selenium version: {selenium.__version__}")
        
        import pandas as pd
        print(f"✅ Pandas version: {pd.__version__}")
        
        import requests
        print(f"✅ Requests version: {requests.__version__}")
        
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup imported successfully")
        
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
        
        # Test our modules
        from utils import validate_ticker, clean_text
        print("✅ utils module imported successfully")
        
        # Test utils functions
        test_ticker = validate_ticker('aapl')
        print(f"✅ Ticker validation works: {test_ticker}")
        
        test_text = clean_text('  Test   Text  ')
        print(f"✅ Text cleaning works: '{test_text}'")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_env_file():
    """Test if .env file exists and can be loaded"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        username = os.getenv('USERNAME')
        password = os.getenv('PASSWORD')
        
        if username and password:
            print(f"✅ .env file loaded successfully")
            print(f"   Username: {username[:5]}***")
            print(f"   Password: ***{password[-3:]}")
            return True
        else:
            print("❌ .env file missing or incomplete")
            return False
            
    except Exception as e:
        print(f"❌ .env file error: {e}")
        return False

def test_chrome_availability():
    """Test if Chrome is available"""
    try:
        import subprocess
        
        # Try to get Chrome version
        result = subprocess.run(
            ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"✅ Chrome available: {result.stdout.strip()}")
            return True
        else:
            print("❌ Chrome not found in standard location")
            return False
            
    except Exception as e:
        print(f"❌ Chrome check error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running simple tests...\n")
    
    tests = [
        ("Module Imports", test_imports),
        ("Environment File", test_env_file),
        ("Chrome Browser", test_chrome_availability)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("📊 Test Results Summary:")
    print("="*50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! The setup looks good.")
        print("You can now try running the full scraper.")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)