# Quick Start Guide - Optimized Web Scraper

## 🚀 First Time Setup
1. Run this setup script: `python setup_optimized_scraper.py`
2. Make sure Chrome browser is installed
3. Add your URLs to `links.txt` (one per line)

## 📊 How to Use
1. **Prepare Excel File**: Create an Excel file with a 'link' column containing URLs
2. **Run Scraper**: Execute `python optimized_scraper.py`
3. **Select File**: Choose your Excel file when prompted
4. **Wait**: The scraper will process URLs with optimized performance

## ⚙️ Performance Features
- **Low CPU/Memory**: Only 2 concurrent workers
- **Batch Processing**: Processes 10 URLs at a time
- **Automatic Logging**: Logs rotate automatically (10MB max)
- **Error Handling**: Screenshots saved for failed pages

## 📋 Files Created
- `optimized_scraper.py` - Main scraper script
- `links.txt` - Your target URLs
- `screenshots/` - Directory for error screenshots
- `*.log` - Log files with rotation

## 🛠️ Troubleshooting
- If ChromeDriver fails: Download manually from chromedriver.chromium.org
- Check `error.log` for detailed error information
- Ensure Excel file has 'link' column

## 📞 Support
Check the logs for errors and refer to the main documentation.
