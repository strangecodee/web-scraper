#!/usr/bin/env python3
"""
Log rotation utility for the web scraping project.
Automatically rotates and archives log files based on size or age.
"""

import os
import glob
import shutil
from datetime import datetime, timedelta
import logging

class LogRotator:
    def __init__(self, max_size_mb=10, max_age_days=7, backup_count=5):
        """
        Initialize log rotator.
        
        Args:
            max_size_mb: Maximum log file size in MB before rotation
            max_age_days: Maximum age in days before rotation
            backup_count: Number of backup files to keep
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_age_days = max_age_days
        self.backup_count = backup_count
        self.log_files = [
            'success.log',
            'error.log', 
            'optimized_scraper.log'
        ]
    
    def should_rotate(self, filepath):
        """Check if a log file should be rotated."""
        if not os.path.exists(filepath):
            return False
            
        # Check size
        file_size = os.path.getsize(filepath)
        if file_size > self.max_size_bytes:
            return True
            
        # Check age
        file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        if datetime.now() - file_mtime > timedelta(days=self.max_age_days):
            return True
            
        return False
    
    def rotate_file(self, filepath):
        """Rotate a single log file."""
        if not os.path.exists(filepath):
            return
            
        # Get all existing backup files
        base_name = os.path.splitext(filepath)[0]
        backup_files = sorted(glob.glob(f"{base_name}.*.log"), reverse=True)
        
        # Remove oldest backups if we have too many
        while len(backup_files) >= self.backup_count:
            os.remove(backup_files.pop())
            backup_files = sorted(glob.glob(f"{base_name}.*.log"), reverse=True)
        
        # Rename existing backups
        for i in range(len(backup_files)-1, -1, -1):
            old_name = backup_files[i]
            new_number = i + 2
            if new_number <= self.backup_count:
                new_name = f"{base_name}.{new_number}.log"
                shutil.move(old_name, new_name)
        
        # Rotate current file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{base_name}.1.log"
        shutil.move(filepath, backup_name)
        
        print(f"Rotated {filepath} -> {backup_name}")
    
    def rotate_all(self):
        """Rotate all log files that need rotation."""
        rotated_count = 0
        
        for log_file in self.log_files:
            if self.should_rotate(log_file):
                self.rotate_file(log_file)
                rotated_count += 1
        
        if rotated_count > 0:
            print(f"Rotated {rotated_count} log file(s)")
        else:
            print("No log files need rotation")
        
        return rotated_count
    
    def cleanup_old_backups(self):
        """Clean up backup files older than max_age_days."""
        cleaned_count = 0
        cutoff_time = datetime.now() - timedelta(days=self.max_age_days)
        
        for log_file in self.log_files:
            base_name = os.path.splitext(log_file)[0]
            backup_files = glob.glob(f"{base_name}.*.log")
            
            for backup_file in backup_files:
                file_mtime = datetime.fromtimestamp(os.path.getmtime(backup_file))
                if file_mtime < cutoff_time:
                    os.remove(backup_file)
                    print(f"Cleaned up old backup: {backup_file}")
                    cleaned_count += 1
        
        return cleaned_count

def setup_rotating_logging():
    """Set up logging with rotation for all log files."""
    # Remove existing handlers to avoid duplicates
    for handler in logging.getLogger().handlers[:]:
        logging.getLogger().removeHandler(handler)
    
    # Set up rotating file handlers
    from logging.handlers import RotatingFileHandler
    
    # Success logger
    success_logger = logging.getLogger('success_logger')
    success_handler = RotatingFileHandler(
        'success.log', 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        mode='a'
    )
    success_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    success_logger.addHandler(success_handler)
    success_logger.setLevel(logging.INFO)
    
    # Error logger
    error_logger = logging.getLogger('error_logger')
    error_handler = RotatingFileHandler(
        'error.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        mode='a'
    )
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    error_logger.addHandler(error_handler)
    error_logger.setLevel(logging.INFO)
    
    # Main logger with rotation
    main_handler = RotatingFileHandler(
        'optimized_scraper.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        mode='a'
    )
    main_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(main_handler)

def main():
    """Main function for manual log rotation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rotate web scraping log files')
    parser.add_argument('--size', type=int, default=10, help='Max size in MB (default: 10)')
    parser.add_argument('--days', type=int, default=7, help='Max age in days (default: 7)')
    parser.add_argument('--backups', type=int, default=5, help='Number of backups to keep (default: 5)')
    parser.add_argument('--cleanup', action='store_true', help='Clean up old backups')
    
    args = parser.parse_args()
    
    rotator = LogRotator(
        max_size_mb=args.size,
        max_age_days=args.days,
        backup_count=args.backups
    )
    
    if args.cleanup:
        cleaned = rotator.cleanup_old_backups()
        print(f"Cleaned up {cleaned} old backup files")
    else:
        rotated = rotator.rotate_all()
        if rotated == 0:
            print("No log files needed rotation")
    
    print("Log rotation complete")

if __name__ == "__main__":
    main()
