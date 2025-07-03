import re
import json
import pandas as pd
import logging
from typing import List, Dict, Any, Optional

def clean_text(text: str) -> str:
    """Clean and normalize text data"""
    if not text:
        return ""
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might interfere with parsing
    text = text.replace('\u00a0', ' ')  # Non-breaking space
    text = text.replace('\u2013', '-')  # En dash
    text = text.replace('\u2014', '-')  # Em dash
    
    return text

def clean_number(value: str) -> str:
    """Clean numeric values while preserving formatting"""
    if not value:
        return ""
    
    # Clean the value but keep commas and dollar signs for readability
    cleaned = clean_text(value)
    
    # Remove parentheses that might indicate negative values
    cleaned = re.sub(r'[()\[\]]', '', cleaned)
    
    return cleaned.strip()

def parse_percentage(value: str) -> str:
    """Parse and clean percentage values"""
    if not value:
        return ""
    
    cleaned = clean_text(value)
    
    # Ensure percentage sign is present
    if '%' not in cleaned and cleaned.replace('.', '').replace('-', '').isdigit():
        cleaned += '%'
    
    return cleaned

def parse_table_row(row_element) -> List[str]:
    """Parse a table row and extract cell data"""
    cells = []
    
    try:
        # Find all td or th elements in the row
        from selenium.webdriver.common.by import By
        cell_elements = row_element.find_elements(By.TAG_NAME, 'td')
        if not cell_elements:
            cell_elements = row_element.find_elements(By.TAG_NAME, 'th')
        
        for cell in cell_elements:
            # Get text content and clean it
            cell_text = clean_text(cell.text)
            cells.append(cell_text)
    
    except Exception as e:
        logging.error(f"Error parsing table row: {e}")
    
    return cells

def extract_quarter_from_text(text: str) -> Optional[str]:
    """Extract quarter information from text"""
    if not text:
        return None
    
    # Look for patterns like "Q1 2024", "Q2 2023", etc.
    quarter_pattern = r'Q[1-4]\s+\d{4}'
    match = re.search(quarter_pattern, text, re.IGNORECASE)
    
    if match:
        return match.group(0)
    
    # Look for patterns like "2024 Q1", "2023 Q2", etc.
    quarter_pattern2 = r'\d{4}\s+Q[1-4]'
    match = re.search(quarter_pattern2, text, re.IGNORECASE)
    
    if match:
        # Reformat to standard format
        parts = match.group(0).split()
        return f"Q{parts[1][1]} {parts[0]}"
    
    return None

def format_holdings_data(holdings_list: List[Dict]) -> List[Dict]:
    """Format and clean holdings data"""
    formatted_holdings = []
    
    for holding in holdings_list:
        formatted_holding = {}
        
        for key, value in holding.items():
            if key.lower() in ['name', 'institution', 'institution_name']:
                formatted_holding['name'] = clean_text(str(value))
            elif key.lower() in ['shares', 'shares_held']:
                formatted_holding['shares'] = clean_number(str(value))
            elif key.lower() in ['value', 'market_value', 'total_value']:
                formatted_holding['value'] = clean_number(str(value))
            elif key.lower() in ['percent', 'percentage', 'percent_portfolio', '% of portfolio']:
                formatted_holding['percent_portfolio'] = parse_percentage(str(value))
            else:
                formatted_holding[key] = clean_text(str(value))
        
        if formatted_holding:  # Only add if not empty
            formatted_holdings.append(formatted_holding)
    
    return formatted_holdings

def save_to_json(data: Dict[str, Any], filepath: str) -> bool:
    """Save data to JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Data saved to {filepath}")
        return True
    
    except Exception as e:
        logging.error(f"Error saving JSON file: {e}")
        return False

def save_to_csv(data: Dict[str, Any], filepath: str) -> bool:
    """Save holdings data to CSV file"""
    try:
        # Save current holdings
        if 'current_holdings' in data and data['current_holdings']:
            current_df = pd.DataFrame(data['current_holdings'])
            current_csv_path = filepath.replace('.csv', '_current.csv')
            current_df.to_csv(current_csv_path, index=False)
            logging.info(f"Current holdings saved to {current_csv_path}")
        
        # Save historical holdings if available
        if 'historical_holdings' in data and data['historical_holdings']:
            historical_df = pd.DataFrame(data['historical_holdings'])
            historical_csv_path = filepath.replace('.csv', '_historical.csv')
            historical_df.to_csv(historical_csv_path, index=False)
            logging.info(f"Historical holdings saved to {historical_csv_path}")
        
        return True
    
    except Exception as e:
        logging.error(f"Error saving CSV file: {e}")
        return False

def validate_ticker(ticker: str) -> str:
    """Validate and format stock ticker"""
    if not ticker:
        raise ValueError("Ticker cannot be empty")
    
    # Clean and uppercase the ticker
    ticker = ticker.strip().upper()
    
    # Basic validation - should be alphanumeric and reasonable length
    if not re.match(r'^[A-Z]{1,5}$', ticker):
        raise ValueError(f"Invalid ticker format: {ticker}")
    
    return ticker

def setup_logging(log_level=logging.INFO):
    """Setup logging configuration"""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('scraper.log')
        ]
    )