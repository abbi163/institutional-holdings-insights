#!/usr/bin/env python3
"""
Institutional Holdings Insights Scraper

A Python application that scrapes institutional holdings data from InsiderMonkey.com
for any given stock ticker and outputs the data in JSON and CSV formats.

Usage:
    python main.py --ticker AAPL
    python main.py --ticker AAPL --output-format json
    python main.py --ticker AAPL --output-format csv
    python main.py --ticker AAPL --output-format both
    python main.py --ticker AAPL --headless false
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from login import InsiderMonkeyLogin
from scraper import InsiderMonkeyScraper
from utils import (
    validate_ticker, save_to_json, save_to_csv, 
    setup_logging
)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Scrape institutional holdings data from InsiderMonkey.com',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --ticker AAPL
  python main.py --ticker MSFT --output-format csv
  python main.py --ticker GOOGL --headless false
        """
    )
    
    parser.add_argument(
        '--ticker', 
        type=str, 
        required=True,
        help='Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)'
    )
    
    parser.add_argument(
        '--output-format',
        choices=['json', 'csv', 'both'],
        default='json',
        help='Output format for the scraped data (default: json)'
    )
    
    parser.add_argument(
        '--headless',
        type=str,
        choices=['true', 'false'],
        default='true',
        help='Run browser in headless mode (default: true)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./data',
        help='Output directory for data files (default: ./data)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    return parser.parse_args()

def ensure_output_directory(output_dir: str) -> str:
    """Ensure output directory exists and return absolute path"""
    # Convert to absolute path
    abs_output_dir = os.path.abspath(output_dir)
    
    # Create directory if it doesn't exist
    Path(abs_output_dir).mkdir(parents=True, exist_ok=True)
    
    return abs_output_dir

def main():
    """Main function to orchestrate the scraping process"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    log_level = getattr(logging, args.log_level)
    setup_logging(log_level)
    
    # Validate ticker
    try:
        ticker = validate_ticker(args.ticker)
    except ValueError as e:
        logging.error(f"Invalid ticker: {e}")
        sys.exit(1)
    
    # Setup output directory
    output_dir = ensure_output_directory(args.output_dir)
    
    # Convert headless argument
    headless = args.headless.lower() == 'true'
    
    logging.info(f"Starting scraping process for ticker: {ticker}")
    logging.info(f"Output directory: {output_dir}")
    logging.info(f"Output format: {args.output_format}")
    logging.info(f"Headless mode: {headless}")
    
    # Initialize login handler
    login_handler = None
    scraper = None
    
    try:
        # Setup and login
        logging.info("Setting up browser and logging in...")
        login_handler = InsiderMonkeyLogin(headless=headless)
        driver = login_handler.setup_driver()
        
        if not login_handler.login():
            logging.error("Login failed. Please check your credentials in .env file.")
            sys.exit(1)
        
        # Initialize scraper
        scraper = InsiderMonkeyScraper(driver)
        
        # Scrape data
        logging.info(f"Scraping institutional holdings data for {ticker}...")
        data = scraper.scrape_all_data(ticker)
        
        if not data['current_holdings'] and not data['historical_holdings']:
            logging.warning(f"No data found for ticker {ticker}")
        
        # Save data based on output format
        base_filename = f"holdings_{ticker}"
        
        if args.output_format in ['json', 'both']:
            json_filepath = os.path.join(output_dir, f"{base_filename}.json")
            if save_to_json(data, json_filepath):
                print(f"✅ JSON data saved to: {json_filepath}")
            else:
                logging.error("Failed to save JSON data")
        
        if args.output_format in ['csv', 'both']:
            csv_filepath = os.path.join(output_dir, f"{base_filename}.csv")
            if save_to_csv(data, csv_filepath):
                print(f"✅ CSV data saved to: {csv_filepath}")
            else:
                logging.error("Failed to save CSV data")
        
        # Print summary
        print(f"\n📊 Scraping Summary for {ticker}:")
        print(f"   Current Holdings: {len(data['current_holdings'])} institutions")
        print(f"   Historical Data: {len(data['historical_holdings'])} quarters")
        
        if data['current_holdings']:
            print(f"\n🏛️  Top 3 Current Holdings:")
            for i, holding in enumerate(data['current_holdings'][:3], 1):
                name = holding.get('name', 'N/A')
                shares = holding.get('shares', 'N/A')
                value = holding.get('value', 'N/A')
                print(f"   {i}. {name}")
                print(f"      Shares: {shares}")
                print(f"      Value: {value}")
        
        logging.info("Scraping process completed successfully!")
        
    except KeyboardInterrupt:
        logging.info("Process interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        logging.error(f"An error occurred during scraping: {e}")
        sys.exit(1)
    
    finally:
        # Clean up
        if login_handler:
            login_handler.close()
        
        logging.info("Browser closed and cleanup completed")

if __name__ == "__main__":
    main()