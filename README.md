# 🧠 Institutional Holdings Insights Scraper

A comprehensive Python application that scrapes institutional holdings data from InsiderMonkey.com for any given stock ticker. The application provides both current and historical institutional holdings data in structured JSON and CSV formats.

## 🎯 Features

- **Automated Login**: Securely logs into InsiderMonkey.com using credentials stored in `.env`
- **Current Holdings**: Scrapes current institutional holdings including:
  - Institution Name
  - Number of Shares
  - Market Value
  - Percentage of Portfolio
- **Historical Data**: Extracts historical institutional holdings for up to 8 quarters
- **Multiple Output Formats**: Supports JSON and CSV output formats
- **Headless Operation**: Can run in headless mode for automated environments
- **Error Handling**: Comprehensive logging and error handling
- **CLI Interface**: Easy-to-use command-line interface

## 📦 Technologies Used

- **Python 3.8+**
- **Selenium** - Browser automation
- **BeautifulSoup4** - HTML parsing
- **Pandas** - Data manipulation and CSV export
- **python-dotenv** - Environment variable management
- **ChromeDriver** - Chrome browser automation
- **webdriver-manager** - Automatic ChromeDriver management

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd institutional-holdings-insights
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables:**
   Create a `.env` file in the root directory with your InsiderMonkey credentials:
   ```env
   USERNAME=your_email@example.com
   PASSWORD=your_password
   ```

## 🔧 Usage

### Basic Usage

```bash
# Scrape data for Apple (AAPL) and save as JSON
python src/main.py --ticker AAPL

# Scrape data for Microsoft (MSFT) and save as CSV
python src/main.py --ticker MSFT --output-format csv

# Scrape data and save in both JSON and CSV formats
python src/main.py --ticker GOOGL --output-format both

# Run with visible browser (non-headless mode)
python src/main.py --ticker TSLA --headless false
```

### Advanced Options

```bash
# Custom output directory
python src/main.py --ticker AAPL --output-dir ./custom_data

# Enable debug logging
python src/main.py --ticker AAPL --log-level DEBUG

# Full command with all options
python src/main.py --ticker AAPL --output-format both --headless true --output-dir ./data --log-level INFO
```

### Command Line Arguments

| Argument | Description | Default | Required |
|----------|-------------|---------|----------|
| `--ticker` | Stock ticker symbol (e.g., AAPL, MSFT) | - | ✅ |
| `--output-format` | Output format: `json`, `csv`, or `both` | `json` | ❌ |
| `--headless` | Run browser in headless mode: `true` or `false` | `true` | ❌ |
| `--output-dir` | Directory to save output files | `../data` | ❌ |
| `--log-level` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` | ❌ |

## 📊 Output Format

### JSON Output Structure

```json
{
  "ticker": "AAPL",
  "current_holdings": [
    {
      "name": "Vanguard Group Inc",
      "shares": "1,400,790,809",
      "value": "$311,157,662,351",
      "percent_portfolio": "5.63%"
    },
    {
      "name": "Blackrock Inc.",
      "shares": "1,038,438,316",
      "value": "$230,555,432,123",
      "percent_portfolio": "4.12%"
    }
  ],
  "historical_holdings": [
    {
      "quarter": "Q2 2024",
      "holdings": [
        {
          "name": "Vanguard Group Inc",
          "shares": "1,350,000,000",
          "value": "$295,000,000,000",
          "percent_portfolio": "5.45%"
        }
      ]
    }
  ]
}
```

### CSV Output

The application generates separate CSV files:
- `holdings_<TICKER>_current.csv` - Current institutional holdings
- `holdings_<TICKER>_historical.csv` - Historical holdings data

## 📁 Project Structure

```
institutional-holdings-insights/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Entry point and CLI interface
│   ├── login.py                 # InsiderMonkey login functionality
│   ├── scraper.py               # Web scraping logic
│   └── utils.py                 # Helper functions and utilities
├── data/
│   ├── .gitkeep                 # Ensures data directory exists
│   └── holdings_<TICKER>.json   # Output data files
├── .env                         # Environment variables (credentials)
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

## 🔐 Security

- **Credentials**: Store login credentials securely in `.env` file
- **Git Ignore**: `.env` file is automatically ignored by git
- **No Hardcoding**: No sensitive information is hardcoded in the source code

## 🐛 Troubleshooting

### Common Issues

1. **Login Failed**
   - Verify credentials in `.env` file
   - Check if InsiderMonkey.com is accessible
   - Ensure account is active and not locked

2. **ChromeDriver Issues**
   - The application automatically manages ChromeDriver
   - Ensure Chrome browser is installed
   - Check internet connection for driver download

3. **No Data Found**
   - Verify the ticker symbol is correct
   - Check if the stock has institutional holdings data
   - Try running in non-headless mode to debug

4. **Permission Errors**
   - Ensure write permissions for output directory
   - Check if output files are not open in other applications

### Debug Mode

Run with debug logging to get detailed information:

```bash
python src/main.py --ticker AAPL --log-level DEBUG --headless false
```

## 📝 Logging

The application creates detailed logs:
- Console output for real-time monitoring
- `scraper.log` file for persistent logging
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational and research purposes. Please respect InsiderMonkey.com's terms of service and robots.txt when using this scraper.

## ⚠️ Disclaimer

- This tool is for educational and research purposes only
- Users are responsible for complying with website terms of service
- The authors are not responsible for any misuse of this tool
- Always respect rate limits and website policies

## 🔮 Future Enhancements

- [ ] Support for multiple tickers via CSV input
- [ ] Flask web API wrapper
- [ ] Database storage integration
- [ ] Real-time data updates
- [ ] Data visualization dashboard
- [ ] Email notifications for significant changes
- [ ] Integration with financial APIs for additional context