<!-- ================= HEADER ================= -->
<p align="center">
  <a href="https://www.linkedin.com/in/annuragmaurya/" target="_blank">
    <img src="https://img.icons8.com/color/48/000000/linkedin.png" width="40"/>
  </a>
  <a href="https://github.com/strangecodee" target="_blank">
    <img src="https://img.icons8.com/fluency/48/github.png" width="40"/>
  </a>
  <a href="mailto:annu.exe@gmail.com" target="_blank">
    <img src="https://img.icons8.com/color/48/gmail-new.png" width="40"/>
  </a>
</p>


# 👋 Hi, I'm Anurag Maurya  
💻 Aspiring Full-Stack Developer | ☁️ Cloud & DevOps Enthusiast  



# 🕸️ Web Scraper – Automated Due Amount Extractor  

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python)  
![Selenium](https://img.shields.io/badge/Selenium-Automation-green.svg?logo=selenium)  
![Status](https://img.shields.io/badge/Status-Active-success.svg)  


## Features

- Extract links from Excel files
- Scrape due amounts from web pages using Selenium
- Multithreaded processing for faster scraping
- Automatic Chrome driver management
- GUI file selection with Tkinter
- Comprehensive logging (success.log and error.log)
- Screenshot capture for failed attempts

## Prerequisites

- Python 3.7+
- Google Chrome browser
- Excel files with a 'link' column containing URLs

## Installation

### Option 1: Automated Setup (Recommended)
```bash
python setup.py
```

### Option 2: Manual Installation
1. Create a virtual environment (optional but recommended):
```bash
python -m venv .venv
# Activate on Windows:
.venv\Scripts\activate
# Activate on Linux/Mac:
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Main Script (Recommended)
```bash
python enhanced_scrape_dues.py
```
- This will open a file dialog to select your Excel file
- It automatically extracts links and starts scraping
- Results are saved back to the original Excel file

### Individual Scripts
```bash
# Extract links from Excel to text file
python extract_links.py

# Basic scraping (requires links.txt)
python scrape_dues.py
```

## File Structure

```
├── enhanced_scrape_dues.py    # Main scraping script with GUI
├── extract_links.py           # Extract links from Excel files
├── scrape_dues.py            # Basic scraping script
├── requirements.txt          # Python dependencies
├── setup.py                 # Automated setup script
├── links.txt               # Extracted URLs (generated)
├── success.log             # Successful scraping results
├── error.log              # Failed scraping attempts
└── screenshots/           # Screenshots of failed pages
```

## Dependencies

- **selenium**: Browser automation
- **pandas**: Excel file handling
- **webdriver-manager**: Automatic Chrome driver management
- **openpyxl**: Excel file operations

## Notes

- The scraper looks for input fields with specific patterns to find due amounts
- Failed attempts are logged and screenshots are saved for debugging
- Multithreading is used for faster processing (default: 5 threads)
- Headless mode is enabled by default for better performance

## ChromeDriver Troubleshooting Guide

### Common ChromeDriver Issues

1. **Version Mismatch**: Chrome updated but ChromeDriver not available yet
2. **Network Issues**: Cannot download ChromeDriver automatically
3. **Permission Issues**: ChromeDriver cannot be executed

### Quick Fixes

#### Option 1: Use the ChromeDriver Fixer Script
```bash
python fix_chrome_driver.py
```
This script will:
- Detect your Chrome version
- Try multiple solutions automatically
- Provide manual download instructions if needed

#### Option 2: Use Enhanced ChromeDriver Manager
```bash
python chrome_driver_manager.py
```
Advanced tool with multiple fallback strategies and automatic compatibility detection.

#### Option 3: Manual ChromeDriver Installation

1. **Check your Chrome version**:
   - Open Chrome → Settings → About Chrome
   - Or run: `google-chrome --version` (Linux/Mac)

2. **Download matching ChromeDriver**:
   - Visit: https://chromedriver.chromium.org/downloads
   - Download version matching your Chrome (e.g., 139.0.7258.x)
   - Extract `chromedriver.exe` (Windows) or `chromedriver` (Linux/Mac)

3. **Place in project folder**:
   - Copy the extracted file to this project directory
   - The scraper will automatically detect it

#### Option 4: Use Compatible Chrome Version
- Install Chrome version 138 or earlier
- ChromeDriver for older versions is more readily available

### Advanced Solutions

#### For Chrome 139.0.7258.x Issues:
Since ChromeDriver 139.x.x may not be available yet, try:

1. **Find compatible version**:
   ```bash
   python fix_chrome_driver.py
   ```
   This will attempt to find the latest compatible version.

2. **Use system PATH**:
   - Download ChromeDriver manually
   - Add it to your system PATH
   - The scraper will use it automatically

3. **Wait for update**:
   - ChromeDriver typically gets updated within 1-2 days of Chrome release
   - Check https://chromedriver.chromium.org/ for updates

### Verification

Test if ChromeDriver is working:
```bash
python test_installation.py
```

### Common Error Messages

- `SessionNotCreatedException`: Version mismatch - use manual installation
- `WebDriverException`: ChromeDriver not found - download manually
- `TimeoutError`: Network issues - try manual download

### Support Files

- `fix_chrome_driver.py`: Automated troubleshooting tool
- `chrome_driver_manager.py`: Enhanced driver management
- `test_installation.py`: Verify ChromeDriver setup

## Output

- Updated Excel file with 'Due Amount' column added
- success.log: Successful scraping results with timestamps
- error.log: Failed attempts with error details
- screenshots/: Visual records of pages that couldn't be processed



<!-- ================= FOOTER ================= -->
<p align="center">
  Made with 💻 by <b>Anurag Maurya</b>  
  <br/>
  <a href="https://www.linkedin.com/in/annuragmaurya/" target="_blank">
    <img src="https://img.icons8.com/color/48/000000/linkedin.png" width="30"/>
  </a>
  <a href="https://github.com/strangecodee" target="_blank">
    <img src="https://img.icons8.com/fluency/48/github.png" width="30"/>
  </a>
  <a href="mailto:annu.exe@gmail.com" target="_blank">
    <img src="https://img.icons8.com/color/48/gmail-new.png" width="30"/>
  </a>
</p>