#!/usr/bin/env python3
"""
Script to modify logging behavior to append instead of overwrite.
This will update both scrapers to preserve log history.
"""

def fix_enhanced_scraper_logging():
    """Fix logging in enhanced_scrape_dues.py to append instead of overwrite."""
    try:
        with open('enhanced_scrape_dues.py', 'r') as f:
            content = f.read()
        
        # Replace FileHandler to use append mode
        new_content = content.replace(
            "success_handler = logging.FileHandler('success.log')",
            "success_handler = logging.FileHandler('success.log', mode='a')"
        )
        new_content = new_content.replace(
            "error_handler = logging.FileHandler('error.log')", 
            "error_handler = logging.FileHandler('error.log', mode='a')"
        )
        
        with open('enhanced_scrape_dues.py', 'w') as f:
            f.write(new_content)
        
        print("✓ Enhanced scraper logging fixed to append mode")
        return True
        
    except Exception as e:
        print(f"✗ Error fixing enhanced scraper: {e}")
        return False

def fix_optimized_scraper_logging():
    """Add proper logging to optimized_scraper.py with append mode."""
    try:
        with open('optimized_scraper.py', 'r') as f:
            content = f.read()
        
        # Add proper file handlers with append mode
        if "FileHandler" not in content:
            # Find the logging setup section
            lines = content.split('\n')
            new_lines = []
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                if "logging.basicConfig" in line and i+1 < len(lines) and "level=logging.INFO" in lines[i+1]:
                    # Add file handlers after basic config
                    new_lines.extend([
                        "",
                        "# File handlers for persistent logging",
                        "file_handler = logging.FileHandler('optimized_scraper.log', mode='a')",
                        "file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))",
                        "logging.getLogger().addHandler(file_handler)",
                        ""
                    ])
            
            new_content = '\n'.join(new_lines)
            
            with open('optimized_scraper.py', 'w') as f:
                f.write(new_content)
            
            print("✓ Optimized scraper logging enhanced with append mode")
            return True
        
        print("✓ Optimized scraper already has proper logging")
        return True
        
    except Exception as e:
        print(f"✗ Error fixing optimized scraper: {e}")
        return False

def main():
    """Main function to fix logging in both scrapers."""
    print("Fixing logging behavior to append instead of overwrite...")
    
    success1 = fix_enhanced_scraper_logging()
    success2 = fix_optimized_scraper_logging()
    
    if success1 and success2:
        print("\n✓ All logging fixes applied successfully!")
        print("Log files will now append instead of overwrite on each run.")
        print("- success.log and error.log will preserve history")
        print("- optimized_scraper.log will track optimized runs")
    else:
        print("\n⚠ Some fixes may not have been applied completely.")

if __name__ == "__main__":
    main()
