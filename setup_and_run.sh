#!/bin/bash

# Institutional Holdings Insights - Setup and Run Script
# This script sets up the conda environment and runs the scraper for AAPL

set -e  # Exit on any error

echo "🚀 Starting Institutional Holdings Insights Setup..."

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Error: conda is not installed or not in PATH"
    echo "Please install Anaconda or Miniconda first"
    exit 1
fi

# Environment name
ENV_NAME="Personal"

echo "🔍 Checking if conda environment '$ENV_NAME' exists..."

# Check if environment exists
if conda env list | grep -q "^$ENV_NAME "; then
    echo "✅ Environment '$ENV_NAME' already exists"
else
    echo "📦 Creating new conda environment '$ENV_NAME'..."
    conda create -n "$ENV_NAME" python=3.9 -y
    echo "✅ Environment '$ENV_NAME' created successfully"
fi

# Activate the environment
echo "🔄 Activating conda environment '$ENV_NAME'..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"

# Verify activation
if [[ "$CONDA_DEFAULT_ENV" != "$ENV_NAME" ]]; then
    echo "❌ Error: Failed to activate environment '$ENV_NAME'"
    exit 1
fi

echo "✅ Environment '$ENV_NAME' activated successfully"

# Install required packages
echo "📦 Installing required Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ All packages installed successfully"

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your InsiderMonkey credentials:"
    echo "USERNAME=your_email@example.com"
    echo "PASSWORD=your_password"
    echo ""
    echo "The script will continue but may fail during login..."
    sleep 3
else
    echo "✅ .env file found"
fi

# Create data directory if it doesn't exist
mkdir -p data

echo "🧪 Testing the scraper with AAPL ticker..."
echo "This may take a few minutes..."
echo ""

# First run a simple test to verify setup
echo "🔍 Running basic setup verification..."
python test_simple.py

if [[ $? -ne 0 ]]; then
    echo "❌ Basic setup test failed. Please check the error messages above."
    exit 1
fi

echo "✅ Basic setup verified successfully!"
echo ""

# Run the scraper for AAPL
echo "🚀 Running the full scraper for AAPL..."
cd src
python main.py --ticker AAPL --output-format both --log-level INFO

# Check if the script completed successfully
if [[ $? -eq 0 ]]; then
    echo ""
    echo "🎉 Success! The scraper completed successfully for AAPL"
    echo "📁 Check the 'data' directory for output files:"
    echo "   - holdings_AAPL.json"
    echo "   - holdings_AAPL_current.csv"
    echo "   - holdings_AAPL_historical.csv (if historical data available)"
    echo ""
    echo "🔧 To run for other tickers, use:"
    echo "   python src/main.py --ticker <TICKER>"
    echo ""
    echo "📖 For more options, see the README.md file"
else
    echo ""
    echo "❌ The scraper encountered an error"
    echo "💡 Troubleshooting tips:"
    echo "   1. Check your .env file credentials"
    echo "   2. Ensure you have a stable internet connection"
    echo "   3. Try running with --headless false for debugging"
    echo "   4. Check the scraper.log file for detailed error information"
    exit 1
fi

echo ""
echo "✨ Setup and test completed successfully!"
echo "Environment '$ENV_NAME' is ready for use."
echo "To activate it manually: conda activate $ENV_NAME"