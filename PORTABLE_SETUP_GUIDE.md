# Portable Optimized Scraper Setup Guide

## 🚀 Quick Setup for New PC

### 1. Prerequisites
- **Python 3.7+**: Download from [python.org](https://python.org)
- **Chrome Browser**: Latest version installed
- **Internet Connection**: For automatic dependency installation

### 2. One-Click Setup
Run the setup script to automate everything:
```bash
python setup_optimized_scraper.py
```

### 3. Manual Setup (Alternative)
If the setup script fails, follow these steps:

#### Install Python Dependencies:
```bash
pip install selenium pandas webdriver-manager openpyxl
```

#### Download ChromeDriver (if automatic fails):
1. Visit: https://chromedriver.chromium.org/
2. Download matching your Chrome version
3. Place `chromedriver.exe` in the project folder

## 📁 Project Structure After Setup
```
web-scraper/
├── portable_optimized_scraper.py  # Main portable scraper
├── setup_optimized_scraper.py     # Setup script
├── links.txt                      # Your target URLs
├── data/
│   └── scraping_results.xlsx      # Auto-created results file
├── logs/
│   ├── optimized_scraper.log      # Current logs
│   └── optimized_scraper.log.1    # Rotated backups
├── screenshots/                   # Error screenshots
└── PORTABLE_SETUP_GUIDE.md        # This guide
```

## 🎯 How to Use

### First Time Setup:
1. **Add URLs**: Edit `links.txt` with your target URLs (one per line)
2. **Run Scraper**: Execute `python portable_optimized_scraper.py`
3. **Choose Option**: Select whether to use existing Excel or create new

### For Existing Excel Files:
- Must contain a column named 'link' with URLs
- Results will be saved back to the same file

### For New Projects:
- Automatically creates `data/scraping_results.xlsx`
- Includes all URLs from `links.txt`

## ⚙️ Features

### Performance Optimizations:
- **Low CPU/Memory**: Only 2 concurrent Chrome instances
- **Batch Processing**: 10 URLs per batch for memory efficiency
- **Automatic Log Rotation**: 10MB max file size, 5 backups kept
- **Error Handling**: Screenshots saved for debugging

### User-Friendly:
- **GUI Dialogs**: Error and information popups
- **Auto ChromeDriver**: Automatic download and setup
- **Progress Tracking**: Real-time logging and batch updates
- **Portable**: No external dependencies needed

## 🔧 Troubleshooting

### Common Issues:

#### ChromeDriver Not Found:
```bash
# Manual fix:
# 1. Check Chrome version: chrome://version/
# 2. Download matching ChromeDriver from chromedriver.chromium.org
# 3. Place chromedriver.exe in project folder
```

#### Dependencies Missing:
```bash
# Manual installation:
pip install selenium pandas webdriver-manager openpyxl
```

#### Excel File Issues:
- Ensure file is not open in another program
- Check that 'link' column exists in Excel

### Log Files:
- Check `logs/optimized_scraper.log` for detailed errors
- View rotated backups: `logs/optimized_scraper.log.1`, `.log.2`, etc.

## 📊 Performance Metrics

- **Memory Usage**: ~100-200MB per Chrome instance
- **CPU Usage**: Minimal (2 workers max)
- **Processing Speed**: ~10-30 URLs per minute (depending on website)
- **Batch Size**: 10 URLs per batch for optimal memory management

## 🗂️ File Management

### Log Rotation:
- Automatic: Files rotate at 10MB
- Manual: `python log_rotation.py --size 10 --days 7 --backups 5`

### Cleaning Up:
```bash
# Clear all logs and backups
rm -f logs/*.log*

# Clear screenshots
rm -f screenshots/*.png

# Keep data but reset everything else
rm -rf logs/ screenshots/
mkdir logs screenshots
```

## 🔄 Scheduled Operation

### Windows Task Scheduler:
1. Create basic task
2. Set trigger (daily/weekly)
3. Action: `python portable_optimized_scraper.py`
4. Start in: Project directory path

### Linux Cron:
```bash
# Edit crontab: crontab -e
# Daily at 2 AM
0 2 * * * cd /path/to/web-scraper && python portable_optimized_scraper.py
```

## 📞 Support

### Quick Checks:
1. **Chrome installed?** `chrome://version/`
2. **Python working?** `python --version`
3. **Dependencies?** `pip list`
4. **URLs in links.txt?** Check file content

### Error Diagnosis:
- Check `logs/optimized_scraper.log`
- Look for error screenshots in `screenshots/`
- Verify ChromeDriver version matches Chrome

### Getting Help:
1. Check logs for specific error messages
2. Ensure all prerequisites are met
3. Verify URLs are accessible in browser
4. Test with a small set of URLs first

## 🎉 Success Tips

1. **Start Small**: Test with 2-3 URLs first
2. **Monitor Logs**: Watch `logs/optimized_scraper.log` in real-time
3. **Check Results**: Verify Excel file updates after each batch
4. **Use Headless**: Runs in background without browser window
5. **Schedule Off-hours**: Run during low-usage times for best performance

The portable optimized scraper is designed to be completely self-contained and easy to set up on any new PC with minimal configuration required.
