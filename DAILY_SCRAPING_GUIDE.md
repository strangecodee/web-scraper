# Daily Scraping Operations Guide

This guide explains how to set up and run daily scraping operations for monitoring changing due amounts.

## 📋 Files Overview

### Core Scraping Files:
- **`daily_scraper.py`** - Enhanced scraper with daily tracking features
- **`enhanced_scrape_dues.py`** - Original scraper (single run)
- **`extract_links.py`** - Link extraction utility

### Scheduling & Automation:
- **`schedule_scraper.py`** - Automated scheduling system
- **`run.bat`** - Windows batch file for manual runs

### Configuration:
- **`requirements.txt`** - Python dependencies
- **`scraper_config.json`** - Auto-generated configuration file

## 🚀 Quick Start for Daily Operations

### Option 1: Manual Daily Run
```bash
python daily_scraper.py
```

### Option 2: Automated Scheduling
```bash
python schedule_scraper.py
```
Then choose option 2 for Windows Task Scheduler setup.

## 📊 Daily Workflow

### 1. **Morning Setup** (9:00 AM recommended)
- Run `daily_scraper.py` or let automated scheduler run
- System will:
  - Scrape all URLs from your Excel file
  - Compare with previous day's data
  - Generate daily change report
  - Archive today's data

### 2. **Review Results**
- Check the main Excel file for updated due amounts
- Review `archive/daily_report_YYYY-MM-DD.xlsx` for changes
- Examine `scraping_YYYYMMDD.log` for detailed logs

### 3. **Troubleshooting**
- Failed URLs are logged in error.log
- Screenshots of failed pages in `screenshots/` folder
- Check archive folder for historical data comparison

## 🔧 Configuration Options

Edit `scraper_config.json` to customize:

```json
{
  "excel_file": "path/to/your/file.xlsx",
  "run_time": "09:00",
  "max_workers": 10,
  "headless": true,
  "notify_on_completion": true
}
```

## 📈 Data Management

### Archive Structure:
```
archive/
├── filename_2024-01-15.xlsx      # Yesterday's data
├── filename_2024-01-16.xlsx      # Today's data
└── daily_report_2024-01-16.xlsx  # Change report
```

### Report Columns:
- `link`: The URL processed
- `Previous Due Amount`: Yesterday's value
- `Current Due Amount`: Today's value  
- `Status`: Changed/Unchanged/New
- `Scrape Date`: Date of processing

## ⚡ Performance Tips

1. **Optimal Run Time**: Schedule during off-peak hours (9:00-10:00 AM)
2. **Worker Count**: Adjust `max_workers` based on your system (5-15)
3. **Headless Mode**: Keep enabled for better performance
4. **Cleanup**: Regularly review archive folder (keep 7-30 days)

## 🛠️ Maintenance

### Weekly Tasks:
- Review and clean `screenshots/` folder
- Backup `archive/` folder
- Check for Chrome driver updates

### Monthly Tasks:
- Review scraping success rates
- Optimize selectors if failure rate increases
- Update dependencies if needed

## ❓ Troubleshooting Common Issues

### Chrome Driver Issues:
```bash
# Reinstall webdriver
pip install --upgrade webdriver-manager
```

### Memory Issues:
- Reduce `max_workers` value
- Close other applications during scraping

### Excel File Locked:
- Ensure Excel is closed before running scraper
- Use file copy if working with shared files

## 📞 Support

For issues:
1. Check logs in `scraping_YYYYMMDD.log`
2. Review screenshots of failed pages
3. Verify Excel file structure has 'link' column

## 🔄 Migration from Single-Run to Daily

If you were using `enhanced_scrape_dues.py`:
1. Your existing Excel file will work with `daily_scraper.py`
2. First run will create baseline data in archive
3. Subsequent runs will track changes automatically

## ⚠️ Important Notes

- Always keep backup of your original Excel file
- Monitor disk space for archive and screenshot folders  
- Test new Excel files with small batches first
- Consider network stability for reliable scraping
