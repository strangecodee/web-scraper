# Logging Behavior Guide

## 📝 Log File Behavior

### Enhanced Scraper (`enhanced_scrape_dues.py`)
- **success.log**: Appends successful scraping results (preserves history)
- **error.log**: Appends failed scraping attempts (preserves history)
- **Main console logs**: Outputs to terminal with timestamps

### Optimized Scraper (`optimized_scraper.py`)
- **optimized_scraper.log**: Appends all logging from optimized runs (preserves history)
- **Main console logs**: Outputs to terminal with performance metrics

## 🔄 Append vs Overwrite Behavior

### Before Fix:
- Log files were **overwritten** on each run
- No history preservation
- Each run started with empty log files

### After Fix:
- Log files now **append** to existing content
- Full history preserved across multiple runs
- Easy to track progress and identify patterns

## 📊 Log File Locations

```
project/
├── success.log          # Successful scraping results (appends)
├── error.log           # Failed scraping attempts (appends)  
├── optimized_scraper.log # Optimized scraper logs (appends)
└── screenshots/        # Screenshots of failed pages
```

## 🎯 Usage Examples

### View Log History:
```bash
# View all successful results
cat success.log

# View all errors  
cat error.log

# View optimized scraper logs
cat optimized_scraper.log

# View logs with timestamps
tail -f success.log
```

### Monitor Live Logging:
```bash
# Watch success logs in real-time
tail -f success.log

# Watch error logs in real-time  
tail -f error.log

# Watch both simultaneously
tail -f success.log error.log
```

## ⚙️ Technical Details

### Enhanced Scraper Logging Setup:
```python
# Appends to success.log
success_handler = logging.FileHandler('success.log', mode='a')

# Appends to error.log  
error_handler = logging.FileHandler('error.log', mode='a')
```

### Optimized Scraper Logging Setup:
```python
# Appends to optimized_scraper.log
file_handler = logging.FileHandler('optimized_scraper.log', mode='a')
```

## 🗑️ Managing Log Files

### To Clear Logs (Start Fresh):
```bash
# Clear all log files
echo "" > success.log
echo "" > error.log  
echo "" > optimized_scraper.log

# Or delete and let them recreate
rm success.log error.log optimized_scraper.log
```

### To Archive Old Logs:
```bash
# Archive logs by date
mv success.log success_$(date +%Y%m%d).log
mv error.log error_$(date +%Y%m%d).log
mv optimized_scraper.log optimized_$(date +%Y%m%d).log
```

## 🔄 Automatic Log Rotation

### Built-in Rotation (Recommended)
Both scrapers now use automatic log rotation:
- **Max file size**: 10MB per log file
- **Backup files**: Keeps 5 backup files (success.log.1, success.log.2, etc.)
- **Automatic**: Rotation happens automatically when files reach size limit

### Manual Log Rotation
```bash
# Rotate logs based on size/age
python log_rotation.py

# Rotate with custom settings
python log_rotation.py --size 20 --days 14 --backups 10

# Clean up old backups only
python log_rotation.py --cleanup
```

### Scheduled Rotation (Windows Task Scheduler)
Create a scheduled task to run daily:
```bash
# Daily rotation at 2 AM
python log_rotation.py --days 7 --backups 5
```

### Scheduled Rotation (Linux Cron)
Add to crontab for daily rotation:
```bash
# Rotate logs daily at 2 AM
0 2 * * * cd /path/to/web-scraper && python log_rotation.py --days 7 --backups 5
```

## 📈 Performance Impact

- **Minimal overhead**: Rotating file handlers have negligible performance impact
- **Disk space management**: Automatic rotation prevents unlimited growth
- **Backup preservation**: Historical data preserved in numbered backup files

## 🔍 Troubleshooting

### If logs aren't rotating:
1. Check file permissions: `ls -la *.log*`
2. Verify maxBytes parameter in RotatingFileHandler setup
3. Check available disk space

### If logs are too large:
1. Use manual rotation: `python log_rotation.py`
2. Adjust maxBytes parameter in code for larger files
3. Increase backupCount for more historical data

### To view rotated logs:
```bash
# View all log files including backups
ls -la *.log*

# View specific backup file
cat success.log.1
cat error.log.2
```

## 🗑️ Managing Rotated Logs

### To Clear All Logs (Start Fresh):
```bash
# Remove all log files and backups
rm -f *.log*
```

### To Archive Rotated Logs:
```bash
# Archive by date
mkdir logs_archive_$(date +%Y%m%d)
mv *.log* logs_archive_$(date +%Y%m%d)/
```

### Monitoring Disk Usage:
```bash
# Check log file sizes
du -h *.log*

# Monitor disk usage over time
df -h .
```
