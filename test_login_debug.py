#!/usr/bin/env python3
"""
Debug login process to understand the page structure
"""

import sys
import os
import time
sys.path.append('src')

def debug_login_page():
    """Debug the login page structure"""
    try:
        print("🔍 Debugging login page structure...")
        
        from login import InsiderMonkeyLogin
        
        # Create login instance with non-headless mode for debugging
        login_handler = InsiderMonkeyLogin(headless=False)
        
        # Setup driver
        driver = login_handler.setup_driver()
        
        if not driver:
            print("❌ Failed to setup driver")
            return False
        
        print("✅ Driver setup successful")
        
        # Navigate to login page
        login_url = "https://www.insidermonkey.com/login/"
        print(f"🌐 Navigating to: {login_url}")
        driver.get(login_url)
        
        # Wait for page to load
        time.sleep(3)
        
        print(f"📄 Current page title: {driver.title}")
        print(f"🔗 Current URL: {driver.current_url}")
        
        # Check for common login form elements
        print("\n🔍 Looking for login form elements...")
        
        # Try different selectors for email/username field
        email_selectors = [
            'input[name="email"]',
            'input[name="username"]', 
            'input[type="email"]',
            'input[id="email"]',
            'input[id="username"]',
            '#email',
            '#username',
            '.email',
            '.username'
        ]
        
        email_found = False
        for selector in email_selectors:
            try:
                elements = driver.find_elements('css selector', selector)
                if elements:
                    print(f"✅ Found email field with selector: {selector}")
                    email_found = True
                    break
            except:
                continue
        
        if not email_found:
            print("❌ No email field found with common selectors")
        
        # Try different selectors for password field
        password_selectors = [
            'input[name="password"]',
            'input[type="password"]',
            'input[id="password"]',
            '#password',
            '.password'
        ]
        
        password_found = False
        for selector in password_selectors:
            try:
                elements = driver.find_elements('css selector', selector)
                if elements:
                    print(f"✅ Found password field with selector: {selector}")
                    password_found = True
                    break
            except:
                continue
        
        if not password_found:
            print("❌ No password field found with common selectors")
        
        # Try different selectors for login button
        button_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:contains("Login")',
            'button:contains("Sign In")',
            '.login-button',
            '.submit-button',
            '#login-button',
            '#submit'
        ]
        
        button_found = False
        for selector in button_selectors:
            try:
                elements = driver.find_elements('css selector', selector)
                if elements:
                    print(f"✅ Found login button with selector: {selector}")
                    button_found = True
                    break
            except:
                continue
        
        if not button_found:
            print("❌ No login button found with common selectors")
        
        # Get page source for manual inspection
        print("\n📝 Saving page source for manual inspection...")
        with open('login_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("✅ Page source saved to 'login_page_source.html'")
        
        # Wait a bit for manual inspection if running in non-headless mode
        print("\n⏳ Waiting 10 seconds for manual inspection...")
        time.sleep(10)
        
        # Clean up
        driver.quit()
        print("✅ Driver cleanup completed")
        
        return email_found and password_found and button_found
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return False

def main():
    """Run login debug"""
    print("🧪 Debugging InsiderMonkey login page...\n")
    
    success = debug_login_page()
    
    if success:
        print("\n🎉 Login form elements found! The selectors should work.")
    else:
        print("\n⚠️  Some login elements not found. Check the saved HTML file.")
        print("\n💡 Next steps:")
        print("   1. Open 'login_page_source.html' in a browser")
        print("   2. Inspect the actual form structure")
        print("   3. Update the selectors in login.py accordingly")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)