#!/usr/bin/env python3
"""
Search for a stock ticker on InsiderMonkey.com and select it
"""

import sys
import os
import time
import argparse
sys.path.append('src')

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Search for a stock ticker on InsiderMonkey.com'
    )
    
    parser.add_argument(
        '--ticker', 
        type=str, 
        required=True,
        help='Stock ticker symbol to search for (e.g., AAPL, MSFT, GOOGL)'
    )
    
    parser.add_argument(
        '--headless',
        type=str,
        choices=['true', 'false'],
        default='false',  # Default to visible browser for debugging
        help='Run browser in headless mode (default: false)'
    )
    
    return parser.parse_args()

def search_ticker(ticker, headless=False):
    """Search for a ticker and select it"""
    try:
        print(f"🔍 Searching for ticker: {ticker}")
        
        from login import InsiderMonkeyLogin
        
        # Create login instance
        login_handler = InsiderMonkeyLogin(headless=headless)
        
        # Setup driver
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
        
        # Wait for page to load after login
        time.sleep(3)
        
        # Look for search box
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        
        wait = WebDriverWait(driver, 10)
        
        # Try different selectors for search box
        search_selectors = [
            "input[type='search']",
            "input[placeholder*='search']",
            "input[placeholder*='Search']",
            "input[name='search']",
            "input[id*='search']",
            "input[class*='search']",
            ".search-input",
            "#search"
        ]
        
        search_box = None
        for selector in search_selectors:
            try:
                print(f"Trying search selector: {selector}")
                search_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                if search_box:
                    print(f"✅ Found search box with selector: {selector}")
                    break
            except:
                continue
        
        if not search_box:
            print("❌ Could not find search box")
            
            # Try to navigate directly to the stock page as fallback
            stock_url = f"https://www.insidermonkey.com/stock/{ticker.lower()}/"
            print(f"Trying direct navigation to: {stock_url}")
            driver.get(stock_url)
            time.sleep(3)
            
            # Check if we landed on a valid page
            if "404" in driver.title or "not found" in driver.title.lower():
                print("❌ Direct navigation failed")
                return False
            else:
                print("✅ Direct navigation successful")
                return True
        
        # Enter ticker in search box
        search_box.clear()
        search_box.send_keys(ticker)
        print(f"✅ Entered ticker: {ticker} in search box")
        
        # Wait for search results to appear
        time.sleep(2)
        
        # Look for ticker in search results
        result_selectors = [
            f"a[href*='{ticker.lower()}']",
            f"a:contains('{ticker}')",
            f".search-result:contains('{ticker}')",
            f"li:contains('{ticker}')"
        ]
        
        result_found = False
        for selector in result_selectors:
            try:
                results = driver.find_elements(By.CSS_SELECTOR, selector)
                for result in results:
                    if ticker.lower() in result.text.lower() or ticker.lower() in result.get_attribute('href').lower():
                        print(f"✅ Found ticker in search results: {result.text}")
                        result.click()
                        print("✅ Clicked on search result")
                        result_found = True
                        break
                if result_found:
                    break
            except:
                continue
        
        if not result_found:
            # Try pressing Enter in the search box
            from selenium.webdriver.common.keys import Keys
            search_box.send_keys(Keys.RETURN)
            print("✅ Pressed Enter in search box")
            time.sleep(3)
            
            # Check if we landed on a search results page
            if ticker.lower() in driver.current_url.lower():
                print("✅ Navigated to search results page")
                
                # Try to find and click on the ticker link
                try:
                    ticker_links = driver.find_elements(By.XPATH, f"//a[contains(text(), '{ticker}')]")
                    if ticker_links:
                        ticker_links[0].click()
                        print(f"✅ Clicked on ticker link: {ticker}")
                        result_found = True
                except:
                    pass
        
        # Wait for page to load after selection
        time.sleep(5)
        
        # Check if we landed on the correct page
        if ticker.lower() in driver.current_url.lower():
            print(f"✅ Successfully navigated to {ticker} page")
            print(f"🔗 Current URL: {driver.current_url}")
            print(f"📄 Page title: {driver.title}")
            return True
        else:
            print(f"❌ Failed to navigate to {ticker} page")
            print(f"🔗 Current URL: {driver.current_url}")
            return False
        
    except Exception as e:
        print(f"❌ Error searching for ticker: {e}")
        return False
    finally:
        # Wait for manual inspection if not headless
        if not headless:
            print("\n⏳ Waiting 15 seconds for manual inspection...")
            time.sleep(15)
        
        # Clean up
        try:
            driver.quit()
            print("✅ Driver cleanup completed")
        except:
            pass

def main():
    """Main function"""
    args = parse_arguments()
    
    # Convert headless argument
    headless = args.headless.lower() == 'true'
    
    print(f"🧪 Searching for ticker: {args.ticker} (Headless: {headless})\n")
    
    success = search_ticker(args.ticker, headless)
    
    if success:
        print(f"\n🎉 Successfully found and selected ticker: {args.ticker}")
    else:
        print(f"\n⚠️ Failed to find or select ticker: {args.ticker}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)