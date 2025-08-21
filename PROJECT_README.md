# Web Scraping Project - Automated Due Amount Extractor

A comprehensive Python-based web scraping tool that extracts due amounts from URLs using Selenium with robust ChromeDriver compatibility handling.

## 🚀 Features

- **Excel Integration**: Extract links from Excel files and update results automatically
- **Multi-threaded Scraping**: Process multiple URLs simultaneously for faster results
- **GUI Interface**: Easy file selection with Tkinter dialogs
- **Comprehensive Logging**: Separate success and error logs with timestamps
- **Screenshot Capture**: Automatic screenshots of failed pages for debugging
- **ChromeDriver Compatibility**: Advanced fallback mechanisms for Chrome version issues
- **Daily Monitoring**: Built-in support for daily scraping and change tracking

## 📋 Prerequisites

- **Python 3.7+**
- **Google Chrome browser** (version 139.0.7258.128 or compatible)
- **Excel files** with a 'link' column containing URLs

## 🛠️ Installation

### Automated Setup (Recommended)
```bash
python setup.py
```

### Manual Installation
1. Create virtual environment:
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🎯 Usage

### Performance-Optimized Scraper (Recommended for Low CPU/Memory)
```bash
python optimized_scraper.py
```
- Uses only 2 concurrent workers (instead of 50)
- Processes in batches of 10 URLs for better memory management
- Reduced window size and disabled images for lower resource usage
- Automatic garbage collection and progress saving

### Main Script (GUI Interface)
```bash
python enhanced_scrape_dues.py
```
- Opens file dialog to select Excel file
- Automatically extracts links and starts scraping
- Updates original Excel file with results

### Individual Components
```bash
# Extract links only
python extract_links.py

# Basic scraping (requires links.txt)
python scrape_dues.py

# Daily monitoring with change tracking
python daily_scraper.py
```

## 🔧 ChromeDriver Compatibility Solutions

### For Chrome 139.0.7258.128 Issues

The project includes advanced ChromeDriver handling with multiple fallback strategies:

1. **Automated Troubleshooting**:
   ```bash
   python fix_chrome_driver.py
   ```

2. **Enhanced Driver Management**:
   ```bash
   python chrome_driver_manager.py
   ```

3. **Manual Installation** (if automated methods fail):
   - Download ChromeDriver from: https://chromedriver.chromium.org/
   - Extract and place `chromedriver.exe` in project folder
   - The system will automatically detect it

### Fallback Strategies Implemented

1. **webdriver_manager**: Automatic ChromeDriver download and management
2. **Local Detection**: Checks for chromedriver.exe in project folder
3. **System PATH**: Uses ChromeDriver from system PATH
4. **Compatible Versions**: Attempts to find version-compatible ChromeDriver
5. **Manual Instructions**: Provides clear download instructions when needed

## 📁 File Structure

```
├── enhanced_scrape_dues.py    # Main scraping script with GUI
├── optimized_scraper.py       # Performance-optimized scraper (low CPU/memory)
├── extract_links.py           # Extract links from Excel files
├── scrape_dues.py            # Basic scraping script
├── daily_scraper.py          # Daily monitoring with change tracking
├── fix_chrome_driver.py      # ChromeDriver troubleshooting tool
├── chrome_driver_manager.py  # Enhanced driver management
├── test_installation.py      # Environment verification
├── requirements.txt          # Python dependencies (compatible with Python 3.7)
├── setup.py                 # Automated setup script
├── links.txt               # Extracted URLs (generated)
├── success.log             # Successful scraping results
├── error.log              # Failed scraping attempts
└── screenshots/           # Screenshots of failed pages
```

## 📦 Dependencies

- **selenium==4.11.2**: Browser automation (Python 3.7 compatible)
- **pandas==1.3.5**: Excel file handling
- **webdriver-manager==3.8.6**: Chrome driver management
- **openpyxl==3.0.10**: Excel file operations

## ⚡ Performance Features

- **Multi-threading**: Default 5 threads (configurable up to 50)
- **Headless Mode**: Enabled by default for better performance
- **Smart Retry**: Multiple selector strategies for robust element finding
- **Memory Management**: Proper driver cleanup after each request

## 🐛 Troubleshooting

### Common Issues

1. **ChromeDriver Not Found**:
   - Run `python fix_chrome_driver.py`
   - Or manually download ChromeDriver

2. **Excel File Format**:
   - Ensure file has 'link' column with valid URLs
   - Supported formats: .xlsx, .xls

3. **Permission Errors**:
   - Run as administrator if needed
   - Check file/folder permissions

### Testing Your Setup

```bash
# Test all dependencies
python test_installation.py

# Test ChromeDriver functionality
python test_chromedriver_fix.py
```

## 📊 Output Files

- **Updated Excel File**: Original file with 'Due Amount' column added
- **success.log**: Timestamped successful scraping results
- **error.log**: Failed attempts with error details
- **screenshots/**: Visual records of pages that couldn't be processed

## 🔄 Daily Monitoring

The `daily_scraper.py` script supports:
- Daily automatic scraping
- Change detection and alerts
- Historical data tracking
- Email notifications (configurable)

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Support

For issues related to ChromeDriver compatibility or scraping functionality, use the built-in troubleshooting tools or check the error logs for detailed information.
