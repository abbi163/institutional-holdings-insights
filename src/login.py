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
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        return self.driver
    
    def login(self):
        """Login to InsiderMonkey website"""
        try:
            logging.info("Starting login process...")
            
            # Navigate to login page
            self.driver.get('https://www.insidermonkey.com/login')
            time.sleep(3)
            
            # Wait for login form to load
            wait = WebDriverWait(self.driver, 10)
            
            # Find and fill username field
            username_field = wait.until(
                EC.presence_of_element_located((By.NAME, 'email'))
            )
            username_field.clear()
            username_field.send_keys(self.username)
            
            # Find and fill password field
            password_field = self.driver.find_element(By.NAME, 'password')
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Submit login form
            login_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if self.is_logged_in():
                logging.info("Login successful!")
                return True
            else:
                logging.error("Login failed - credentials may be incorrect")
                return False
                
        except TimeoutException:
            logging.error("Login timeout - page elements not found")
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