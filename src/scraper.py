import time
import logging
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from .utils import (
    clean_text, clean_number, parse_percentage, 
    parse_table_row, extract_quarter_from_text,
    format_holdings_data
)

class InsiderMonkeyScraper:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)
    
    def navigate_to_stock_page(self, ticker: str) -> bool:
        """Navigate to the institutional holdings page for a given ticker"""
        try:
            # Construct URL for institutional holdings page
            url = f"https://www.insidermonkey.com/insider-trading/company/{ticker}/"
            
            logging.info(f"Navigating to {url}")
            self.driver.get(url)
            time.sleep(3)
            
            # Check if page loaded successfully
            if "404" in self.driver.title or "not found" in self.driver.title.lower():
                logging.error(f"Stock page not found for ticker: {ticker}")
                return False
            
            # Look for institutional holdings section
            try:
                # Try to find institutional holdings link or section
                institutional_link = self.driver.find_element(
                    By.XPATH, 
                    "//a[contains(text(), 'Institutional') or contains(text(), 'Holdings')]"
                )
                institutional_link.click()
                time.sleep(3)
            except NoSuchElementException:
                # If direct link not found, try alternative URL
                institutional_url = f"https://www.insidermonkey.com/insider-trading/company/{ticker}/institutional-investors/"
                logging.info(f"Trying alternative URL: {institutional_url}")
                self.driver.get(institutional_url)
                time.sleep(3)
            
            return True
            
        except Exception as e:
            logging.error(f"Error navigating to stock page: {e}")
            return False
    
    def scrape_current_holdings(self) -> List[Dict[str, str]]:
        """Scrape current institutional holdings from the page"""
        holdings = []
        
        try:
            logging.info("Scraping current institutional holdings...")
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Look for tables containing institutional holdings
            tables = soup.find_all('table')
            
            for table in tables:
                # Check if this table contains institutional holdings
                headers = table.find_all('th')
                header_texts = [clean_text(th.get_text()) for th in headers]
                
                # Look for expected column headers
                if any(keyword in ' '.join(header_texts).lower() 
                       for keyword in ['institution', 'shares', 'value', 'portfolio']):
                    
                    holdings = self._parse_holdings_table(table)
                    if holdings:
                        break
            
            # If no table found, try alternative selectors
            if not holdings:
                holdings = self._scrape_holdings_alternative_method()
            
            logging.info(f"Found {len(holdings)} current holdings")
            return format_holdings_data(holdings)
            
        except Exception as e:
            logging.error(f"Error scraping current holdings: {e}")
            return []
    
    def _parse_holdings_table(self, table) -> List[Dict[str, str]]:
        """Parse a holdings table and extract data"""
        holdings = []
        
        try:
            rows = table.find_all('tr')
            if not rows:
                return holdings
            
            # Get headers
            header_row = rows[0]
            headers = [clean_text(th.get_text()) for th in header_row.find_all(['th', 'td'])]
            
            # Map headers to standard field names
            header_mapping = self._create_header_mapping(headers)
            
            # Process data rows
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:  # Minimum expected columns
                    
                    row_data = {}
                    for i, cell in enumerate(cells):
                        if i < len(headers):
                            field_name = header_mapping.get(i, f"column_{i}")
                            cell_text = clean_text(cell.get_text())
                            
                            if field_name and cell_text:
                                row_data[field_name] = cell_text
                    
                    if row_data and 'name' in row_data:
                        holdings.append(row_data)
        
        except Exception as e:
            logging.error(f"Error parsing holdings table: {e}")
        
        return holdings
    
    def _create_header_mapping(self, headers: List[str]) -> Dict[int, str]:
        """Create mapping from column index to standard field names"""
        mapping = {}
        
        for i, header in enumerate(headers):
            header_lower = header.lower()
            
            if any(keyword in header_lower for keyword in ['institution', 'name', 'fund']):
                mapping[i] = 'name'
            elif any(keyword in header_lower for keyword in ['shares', 'share']):
                mapping[i] = 'shares'
            elif any(keyword in header_lower for keyword in ['value', 'market']):
                mapping[i] = 'value'
            elif any(keyword in header_lower for keyword in ['percent', '%', 'portfolio']):
                mapping[i] = 'percent_portfolio'
        
        return mapping
    
    def _scrape_holdings_alternative_method(self) -> List[Dict[str, str]]:
        """Alternative method to scrape holdings if table parsing fails"""
        holdings = []
        
        try:
            # Look for div-based layouts or other structures
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Try to find holdings in div containers
            holding_containers = soup.find_all('div', class_=lambda x: x and 
                                               any(keyword in x.lower() for keyword in 
                                                   ['holding', 'institution', 'investor']))
            
            for container in holding_containers:
                # Extract text and try to parse structured data
                text = clean_text(container.get_text())
                
                # Look for patterns that might indicate holdings data
                if any(keyword in text.lower() for keyword in ['shares', 'value', '%']):
                    # This would need more specific parsing based on actual page structure
                    pass
        
        except Exception as e:
            logging.error(f"Error in alternative scraping method: {e}")
        
        return holdings
    
    def scrape_historical_holdings(self) -> List[Dict[str, Any]]:
        """Scrape historical institutional holdings for the last 8 quarters"""
        historical_data = []
        
        try:
            logging.info("Scraping historical institutional holdings...")
            
            # Look for historical data section or tabs
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Try to find historical data tables or sections
            historical_sections = soup.find_all(['div', 'section'], 
                                                class_=lambda x: x and 
                                                any(keyword in x.lower() for keyword in 
                                                    ['historical', 'quarter', 'trend']))
            
            for section in historical_sections:
                quarters_data = self._parse_historical_section(section)
                historical_data.extend(quarters_data)
            
            # If no historical sections found, look for tabs or links
            if not historical_data:
                historical_data = self._scrape_historical_from_tabs()
            
            # Limit to last 8 quarters
            historical_data = historical_data[:8]
            
            logging.info(f"Found historical data for {len(historical_data)} quarters")
            return historical_data
            
        except Exception as e:
            logging.error(f"Error scraping historical holdings: {e}")
            return []
    
    def _parse_historical_section(self, section) -> List[Dict[str, Any]]:
        """Parse historical data from a section"""
        quarters_data = []
        
        try:
            # Look for tables within the section
            tables = section.find_all('table')
            
            for table in tables:
                # Try to extract quarter information
                quarter_text = section.get_text()
                quarter = extract_quarter_from_text(quarter_text)
                
                if quarter:
                    holdings = self._parse_holdings_table(table)
                    if holdings:
                        quarter_data = {
                            'quarter': quarter,
                            'holdings': holdings
                        }
                        quarters_data.append(quarter_data)
        
        except Exception as e:
            logging.error(f"Error parsing historical section: {e}")
        
        return quarters_data
    
    def _scrape_historical_from_tabs(self) -> List[Dict[str, Any]]:
        """Try to scrape historical data from tabs or interactive elements"""
        historical_data = []
        
        try:
            # Look for tab elements or buttons that might show historical data
            tab_elements = self.driver.find_elements(
                By.XPATH, 
                "//button[contains(text(), 'Q') or contains(text(), 'Quarter')] | "
                "//a[contains(text(), 'Q') or contains(text(), 'Quarter')]"
            )
            
            for tab in tab_elements[:8]:  # Limit to 8 quarters
                try:
                    # Click on the tab
                    self.driver.execute_script("arguments[0].click();", tab)
                    time.sleep(2)
                    
                    # Extract quarter information
                    quarter = extract_quarter_from_text(tab.text)
                    
                    if quarter:
                        # Scrape holdings for this quarter
                        holdings = self.scrape_current_holdings()
                        
                        if holdings:
                            quarter_data = {
                                'quarter': quarter,
                                'holdings': holdings
                            }
                            historical_data.append(quarter_data)
                
                except Exception as e:
                    logging.error(f"Error clicking tab: {e}")
                    continue
        
        except Exception as e:
            logging.error(f"Error scraping from tabs: {e}")
        
        return historical_data
    
    def scrape_all_data(self, ticker: str) -> Dict[str, Any]:
        """Scrape all institutional holdings data for a ticker"""
        result = {
            'ticker': ticker.upper(),
            'current_holdings': [],
            'historical_holdings': []
        }
        
        try:
            # Navigate to stock page
            if not self.navigate_to_stock_page(ticker):
                return result
            
            # Scrape current holdings
            current_holdings = self.scrape_current_holdings()
            result['current_holdings'] = current_holdings
            
            # Scrape historical holdings
            historical_holdings = self.scrape_historical_holdings()
            result['historical_holdings'] = historical_holdings
            
            logging.info(f"Scraping completed for {ticker}")
            
        except Exception as e:
            logging.error(f"Error scraping data for {ticker}: {e}")
        
        return result