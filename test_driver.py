#!/usr/bin/env python3
"""
Test ChromeDriver setup specifically
"""

import sys
import os
sys.path.append('src')

def test_chromedriver():
    """Test ChromeDriver setup"""
    try:
        print("🔧 Testing ChromeDriver setup...")
        
        from login import InsiderMonkeyLogin
        
        # Create login instance
        login_handler = InsiderMonkeyLogin(headless=True)
        
        # Try to setup driver
        driver = login_handler.setup_driver()
        
        if driver:
            print("✅ ChromeDriver setup successful!")
            
            # Test basic navigation
            print("🌐 Testing basic navigation...")
            driver.get("https://www.google.com")
            
            title = driver.title
            print(f"✅ Navigation successful! Page title: {title}")
            
            # Clean up
            driver.quit()
            print("✅ Driver cleanup successful!")
            
            return True
        else:
            print("❌ ChromeDriver setup failed - no driver returned")
            return False
            
    except Exception as e:
        print(f"❌ ChromeDriver test failed: {e}")
        return False

def main():
    """Run ChromeDriver test"""
    print("🧪 Testing ChromeDriver setup...\n")
    
    success = test_chromedriver()
    
    if success:
        print("\n🎉 ChromeDriver test passed! The browser automation is working.")
    else:
        print("\n⚠️  ChromeDriver test failed. Please check the error messages above.")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure Google Chrome is installed")
        print("   2. Check your internet connection")
        print("   3. Try running: brew install chromedriver")
        print("   4. Or download ChromeDriver manually from https://chromedriver.chromium.org/")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)