#!/usr/bin/env python3
"""
Scheduling script for daily automated scraping.
Run this script to set up scheduled daily runs.
"""

import os
import sys
import subprocess
import schedule
import time
from datetime import datetime
import json

def load_config():
    """Load configuration from config file."""
    config_file = 'scraper_config.json'
    default_config = {
        "excel_file": "",  # Will be set by user
        "run_time": "09:00",  # Default run time: 9:00 AM
        "max_workers": 10,
        "headless": True,
        "notify_on_completion": True
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return {**default_config, **json.load(f)}
        except:
            print("Error reading config file, using defaults")
    
    return default_config

def save_config(config):
    """Save configuration to file."""
    with open('scraper_config.json', 'w') as f:
        json.dump(config, f, indent=2)

def setup_schedule():
    """Set up the daily scraping schedule."""
    config = load_config()
    
    print("=" * 50)
    print("DAILY SCRAPING SCHEDULER SETUP")
    print("=" * 50)
    
    # Get Excel file path if not set
    if not config['excel_file'] or not os.path.exists(config['excel_file']):
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()
        print("Please select the Excel file for daily scraping...")
        excel_file = filedialog.askopenfilename(
            title="Select Excel File for Daily Scraping",
            filetypes=[("Excel files", "*.xlsx;*.xls")]
        )
        
        if not excel_file:
            print("No file selected. Exiting.")
            return False
            
        config['excel_file'] = excel_file
        save_config(config)
    
    # Get run time
    print(f"\nCurrent scheduled time: {config['run_time']}")
    new_time = input("Enter new run time (HH:MM, or press Enter to keep current): ").strip()
    if new_time:
        # Validate time format
        try:
            datetime.strptime(new_time, '%H:%M')
            config['run_time'] = new_time
            save_config(config)
        except ValueError:
            print("Invalid time format. Using current time.")
    
    print(f"\nScheduled to run daily at {config['run_time']}")
    print(f"Excel file: {config['excel_file']}")
    print(f"Max workers: {config['max_workers']}")
    
    return True

def run_daily_scrape():
    """Run the daily scraping task."""
    config = load_config()
    
    if not config['excel_file'] or not os.path.exists(config['excel_file']):
        print("Error: Excel file not found in config.")
        return
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting scheduled scrape...")
    
    try:
        # Run the daily scraper
        result = subprocess.run([
            sys.executable, 'daily_scraper.py'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        print(f"Scraping completed with return code: {result.returncode}")
        
        if result.stdout:
            print("Output:", result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
            
        # Send notification (you can integrate with email/telegram here)
        if config['notify_on_completion']:
            print("Notification: Daily scraping completed")
            
    except Exception as e:
        print(f"Error running scraper: {e}")

def create_windows_task():
    """Create a Windows scheduled task for automation."""
    print("\nCreating Windows Scheduled Task...")
    
    try:
        # Get the full path to the Python executable and script
        python_exe = sys.executable
        script_path = os.path.join(os.getcwd(), 'schedule_scraper.py')
        
        # Create a batch file to run the script
        batch_content = f'''@echo off
echo Running daily scraper...
"{python_exe}" "{script_path}" --run-now
pause
'''
        
        with open('run_daily.bat', 'w') as f:
            f.write(batch_content)
        
        print("Created batch file: run_daily.bat")
        print("\nTo set up Windows Task Scheduler manually:")
        print("1. Open Task Scheduler")
        print("2. Create Basic Task")
        print("3. Set trigger to daily at your desired time")
        print("4. Action: Start a program")
        print("5. Program/script: run_daily.bat")
        print("6. Start in: {}".format(os.getcwd()))
        
    except Exception as e:
        print(f"Error creating Windows task: {e}")

def main():
    """Main function for scheduling."""
    if len(sys.argv) > 1 and sys.argv[1] == '--run-now':
        run_daily_scrape()
        return
    
    if not setup_schedule():
        return
    
    print("\nChoose scheduling method:")
    print("1. Run with Python scheduler (requires script to be running)")
    print("2. Set up Windows Task Scheduler (recommended for production)")
    print("3. Run now for testing")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        print("\nStarting Python scheduler...")
        print("Press Ctrl+C to stop")
        
        config = load_config()
        schedule.every().day.at(config['run_time']).do(run_daily_scrape)
        
        # Run immediately for testing
        run_daily_scrape()
        
        while True:
            schedule.run_pending()
            time.sleep(60)
            
    elif choice == '2':
        create_windows_task()
        
    elif choice == '3':
        run_daily_scrape()
        
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
