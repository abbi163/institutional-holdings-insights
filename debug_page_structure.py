#!/usr/bin/env python3
"""
Debug the actual page structure for AAPL institutional holdings
"""

import sys
import os
import time
sys.path.append('src')

def debug_aapl_page():
    """Debug the AAPL institutional holdings page structure"""
    try:
        print("🔍 Debugging AAPL institutional holdings page...")
        
        from login import InsiderMonkeyLogin
        
        # Create login instance with non-headless mode for debugging
        login_handler = InsiderMonkeyLogin(headless=False)
        
        # Setup driver and login
        driver = login_handler.setup_driver()
        
        if not driver:
            print("❌ Failed to setup driver")
            return False
        
        print("✅ Driver setup successful")
        
        # Login first
        if not login_handler.login():
            print("❌ Login failed")
            return False
        
        print("✅ Login successful")
        
        # Navigate to AAPL page
        urls_to_try = [
            "https://www.insidermonkey.com/insider-trading/company/AAPL/",
            "https://www.insidermonkey.com/insider-trading/company/AAPL/institutional-investors/",
            "https://www.insidermonkey.com/hedge-fund-stock-picks/AAPL/",
            "https://www.insidermonkey.com/stock/apple-inc/AAPL/"
        ]
        
        for i, url in enumerate(urls_to_try, 1):
            print(f"\n🌐 Trying URL {i}: {url}")
            driver.get(url)
            time.sleep(3)
            
            print(f"📄 Page title: {driver.title}")
            print(f"🔗 Current URL: {driver.current_url}")
            
            # Check for 404 or error pages
            if "404" in driver.title or "not found" in driver.title.lower():
                print("❌ Page not found")
                continue
            
            # Save page source for inspection
            filename = f"aapl_page_{i}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print(f"✅ Page source saved to '{filename}'")
            
            # Look for tables
            from selenium.webdriver.common.by import By
            tables = driver.find_elements(By.TAG_NAME, "table")
            print(f"📊 Found {len(tables)} tables on the page")
            
            # Look for specific keywords in page content
            page_text = driver.page_source.lower()
            keywords = ['institutional', 'holdings', 'shares', 'portfolio', 'investor', 'fund']
            found_keywords = [kw for kw in keywords if kw in page_text]
            print(f"🔍 Found keywords: {found_keywords}")
            
            # Look for links that might lead to institutional data
            links = driver.find_elements(By.TAG_NAME, "a")
            institutional_links = []
            for link in links:
                try:
                    link_text = link.text.lower()
                    href = link.get_attribute('href') or ''
                    if any(kw in link_text for kw in ['institutional', 'holdings', 'investor']) or \
                       any(kw in href.lower() for kw in ['institutional', 'holdings', 'investor']):
                        institutional_links.append((link_text, href))
                except:
                    continue
            
            print(f"🔗 Found {len(institutional_links)} institutional-related links:")
            for text, href in institutional_links[:5]:  # Show first 5
                print(f"   - '{text}' -> {href}")
            
            # If we found relevant content, break
            if found_keywords and ('institutional' in found_keywords or 'holdings' in found_keywords):
                print(f"\n✅ Found relevant content on URL {i}")
                break
        
        # Wait for manual inspection
        print("\n⏳ Waiting 15 seconds for manual inspection...")
        time.sleep(15)
        
        # Clean up
        driver.quit()
        print("✅ Driver cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return False

def main():
    """Run AAPL page debug"""
    print("🧪 Debugging AAPL institutional holdings page structure...\n")
    
    success = debug_aapl_page()
    
    if success:
        print("\n🎉 Debug completed! Check the saved HTML files for page structure.")
    else:
        print("\n⚠️  Debug failed. Check the error messages above.")
    
    print("\n💡 Next steps:")
    print("   1. Open the saved HTML files in a browser")
    print("   2. Look for institutional holdings tables or sections")
    print("   3. Update the scraper selectors accordingly")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)