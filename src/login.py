import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class InsiderMonkeyLogin:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.username = os.getenv('USERNAME')
        self.password = os.getenv('PASSWORD')
        
        if not self.username or not self.password:
            raise ValueError("Username and password must be set in .env file")
    
    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Install and setup ChromeDriver
        try:
            driver_path = ChromeDriverManager().install()
            
            # Fix for webdriver-manager path issues
            if 'THIRD_PARTY_NOTICES' in driver_path or not driver_path.endswith('chromedriver'):
                import os
                import stat
                
                driver_dir = os.path.dirname(driver_path)
                # Look for the actual chromedriver executable
                possible_paths = [
                    os.path.join(driver_dir, 'chromedriver'),
                    os.path.join(os.path.dirname(driver_dir), 'chromedriver'),
                    os.path.join(driver_dir, 'chromedriver-mac-arm64', 'chromedriver')
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        driver_path = path
                        # Make sure it's executable
                        os.chmod(driver_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                        break
            
            logging.info(f"Using ChromeDriver at: {driver_path}")
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
        except Exception as e:
            logging.error(f"ChromeDriver setup failed: {e}")
            # Fallback: try to use system chromedriver
            try:
                logging.info("Trying fallback to system ChromeDriver...")
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as fallback_error:
                logging.error(f"Fallback ChromeDriver also failed: {fallback_error}")
                raise Exception("Could not initialize ChromeDriver. Please ensure Chrome is installed and ChromeDriver is available.")
        
        return self.driver
    
    def login(self):
        """Login to InsiderMonkey website"""
        try:
            logging.info("Starting login process...")
            
            # Navigate to login page
            self.driver.get('https://www.insidermonkey.com/login/')
            time.sleep(3)
            
            # Wait for login form to load
            wait = WebDriverWait(self.driver, 15)
            
            logging.info("Looking for email field...")
            # Find and fill email field using the correct selector
            email_field = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
            )
            email_field.clear()
            email_field.send_keys(self.username)
            logging.info("Email field filled successfully")
            
            # Find and fill password field
            logging.info("Looking for password field...")
            password_field = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
            )
            password_field.clear()
            password_field.send_keys(self.password)
            logging.info("Password field filled successfully")
            
            # Submit login form
            logging.info("Looking for submit button...")
            login_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))
            )
            login_button.click()
            logging.info("Login button clicked")
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if self.is_logged_in():
                logging.info("Login successful!")
                return True
            else:
                logging.error("Login failed - credentials may be incorrect")
                return False
                
        except TimeoutException as e:
            logging.error(f"Login timeout - page elements not found: {e}")
            return False
        except NoSuchElementException as e:
            logging.error(f"Login element not found: {e}")
            return False
        except Exception as e:
            logging.error(f"Login error: {e}")
            return False
    
    def is_logged_in(self):
        """Check if user is successfully logged in"""
        try:
            # Look for elements that indicate successful login
            # This might need adjustment based on actual website structure
            current_url = self.driver.current_url
            
            # Check if we're redirected away from login page
            if 'login' not in current_url.lower():
                return True
            
            # Alternative: look for user-specific elements
            try:
                self.driver.find_element(By.XPATH, '//a[contains(@href, "logout") or contains(text(), "Logout")]')
                return True
            except NoSuchElementException:
                pass
            
            return False
            
        except Exception as e:
            logging.error(f"Error checking login status: {e}")
            return False
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            logging.info("Browser closed")