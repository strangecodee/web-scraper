#!/usr/bin/env python3
"""
Enhanced web scraper for daily due amount monitoring.
Tracks changes over time and provides daily comparison reports.
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime, timedelta
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil

# Set up logging
if not os.path.exists('screenshots'):
    os.makedirs('screenshots')
if not os.path.exists('archive'):
    os.makedirs('archive')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'scraping_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

class DailyDueScraper:
    def __init__(self, headless=True):
        """Initialize the scraper with Chrome options."""
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        self.today = datetime.now().strftime('%Y-%m-%d')
        
    def get_driver(self):
        """Create and return a Chrome driver instance."""
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )
    
    def extract_due_amount(self, url):
        """Extract due amount from the specific input field."""
        driver = None
        screenshot_path = None
        try:
            driver = self.get_driver()
            logging.info(f"Processing URL: {url}")

            driver.get(url)

            # Wait for the page to load
            wait = WebDriverWait(driver, 15)

            # Try multiple selectors to find the due amount input field
            selectors = [
                "input[name='totalDue']",
                "input[id*=':r']",
                "input[aria-invalid='false'][disabled]",
                "input.MuiInputBase-input.MuiFilledInput-input.Mui-disabled",
                "input[value*='8051']",
                "//input[@name='totalDue']",
                "//input[contains(@id, ':r') and @disabled]",
                "//input[@aria-invalid='false' and @disabled]"
            ]

            due_amount = None

            # Try CSS selectors first
            for selector in selectors[:5]:
                try:
                    element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    due_amount = element.get_attribute('value')
                    if due_amount:
                        logging.info(f"Found due amount via CSS: {due_amount}")
                        break
                except:
                    continue

            # Try XPath selectors if CSS didn't work
            if not due_amount:
                for xpath in selectors[5:]:
                    try:
                        element = wait.until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )
                        due_amount = element.get_attribute('value')
                        if due_amount:
                            logging.info(f"Found due amount via XPath: {due_amount}")
                            break
                    except:
                        continue

            # Fallback: try to find any input with value attribute
            if not due_amount:
                try:
                    inputs = driver.find_elements(By.TAG_NAME, 'input')
                    for input_elem in inputs:
                        value = input_elem.get_attribute('value')
                        if value and value.isdigit():
                            due_amount = value
                            logging.info(f"Found due amount via fallback: {due_amount}")
                            break
                except:
                    pass

            # Only save screenshot if not found (considered failed)
            if not due_amount:
                screenshot_path = os.path.join('screenshots', f"notfound_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                driver.save_screenshot(screenshot_path)

            return due_amount if due_amount else "Not found"

        except TimeoutException:
            logging.error(f"Timeout loading URL: {url}")
            screenshot_path = os.path.join('screenshots', f"timeout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            if driver:
                driver.save_screenshot(screenshot_path)
            return "Timeout"
        except Exception as e:
            logging.error(f"Error processing {url}: {str(e)}")
            screenshot_path = os.path.join('screenshots', f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            if driver:
                driver.save_screenshot(screenshot_path)
            return f"Error: {str(e)}"
        finally:
            if driver:
                driver.quit()
    
    def load_previous_data(self, excel_file):
        """Load previous day's data for comparison."""
        previous_day = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        archive_file = os.path.join('archive', f"{os.path.splitext(os.path.basename(excel_file))[0]}_{previous_day}.xlsx")
        
        if os.path.exists(archive_file):
            try:
                return pd.read_excel(archive_file)
            except:
                logging.warning(f"Could not load previous data from {archive_file}")
        return None
    
    def archive_current_data(self, df, excel_file):
        """Archive today's data for future reference."""
        archive_file = os.path.join('archive', f"{os.path.splitext(os.path.basename(excel_file))[0]}_{self.today}.xlsx")
        df.to_excel(archive_file, index=False)
        logging.info(f"Data archived to {archive_file}")
    
    def generate_daily_report(self, current_df, previous_df, excel_file):
        """Generate a daily comparison report."""
        if previous_df is None:
            logging.info("No previous data available for comparison")
            return
        
        report_data = []
        changes_count = 0
        
        for idx, current_row in current_df.iterrows():
            link = current_row['link']
            current_due = current_row.get('Due Amount', '')
            previous_row = previous_df[previous_df['link'] == link]
            
            if not previous_row.empty:
                previous_due = previous_row.iloc[0].get('Due Amount', '')
                status = 'Changed' if str(current_due) != str(previous_due) else 'Unchanged'
                if status == 'Changed':
                    changes_count += 1
            else:
                previous_due = 'N/A'
                status = 'New'
                changes_count += 1
            
            report_data.append({
                'link': link,
                'Previous Due Amount': previous_due,
                'Current Due Amount': current_due,
                'Status': status,
                'Scrape Date': self.today
            })
        
        report_df = pd.DataFrame(report_data)
        report_file = os.path.join('archive', f"daily_report_{self.today}.xlsx")
        report_df.to_excel(report_file, index=False)
        
        logging.info(f"Daily report generated: {changes_count} changes detected")
        logging.info(f"Report saved to {report_file}")
        
        return report_df
    
    def process_links_daily(self, input_file='links.txt', excel_file=None, max_workers=5):
        """Process links with daily tracking and comparison."""
        try:
            # Read links from file
            with open(input_file, 'r', encoding='utf-8') as f:
                links = [line.strip() for line in f if line.strip() and str(line.strip()).lower() != 'nan']

            logging.info(f"Found {len(links)} valid links to process")

            # Load the Excel file
            df_excel = pd.read_excel(excel_file)
            if 'link' not in df_excel.columns:
                logging.error("Excel file does not contain 'link' column.")
                return None

            # Load previous day's data
            previous_df = self.load_previous_data(excel_file)

            # Prepare a mapping from link to index for fast update
            link_to_index = {str(row['link']).strip(): idx for idx, row in df_excel.iterrows()}

            # Add date column if it doesn't exist
            if 'Last Scraped' not in df_excel.columns:
                df_excel['Last Scraped'] = ''

            results = []
            failed_links = []

            def scrape_link(link):
                due_amount = self.extract_due_amount(link)
                result = {
                    'link': link,
                    'Due Amount': due_amount,
                    'Status': 'Success' if due_amount and due_amount != 'Not found' and not due_amount.startswith('Error') else 'Failed',
                    'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                return result

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_link = {executor.submit(scrape_link, link): link for link in links}
                for idx, future in enumerate(as_completed(future_to_link), 1):
                    link = future_to_link[future]
                    try:
                        result = future.result()
                        results.append(result)
                        logging.info(f"Processed {idx}/{len(links)}: {link}")
                        
                        # Update Excel DataFrame
                        if link in link_to_index:
                            df_excel.at[link_to_index[link], 'Due Amount'] = result['Due Amount']
                            df_excel.at[link_to_index[link], 'Last Scraped'] = self.today
                        
                    except Exception as exc:
                        logging.error(f"Exception for {link}: {exc}")
                        failed_links.append(link)

            # Save updated Excel file
            df_excel.to_excel(excel_file, index=False)
            
            # Archive today's data
            self.archive_current_data(df_excel, excel_file)
            
            # Generate daily report
            report_df = self.generate_daily_report(df_excel, previous_df, excel_file)

            logging.info(f"Daily scraping complete! Results updated in {excel_file}")
            logging.info(f"Total processed: {len(results)}")
            logging.info(f"Successful: {len([r for r in results if r['Status'] == 'Success'])}")
            logging.info(f"Failed: {len(failed_links)}")

            if failed_links:
                logging.info(f"Failed links: {failed_links}")

            return df_excel, report_df

        except FileNotFoundError:
            logging.error(f"Input file {input_file} or Excel file {excel_file} not found")
            return None, None
        except Exception as e:
            logging.error(f"Error processing links: {str(e)}")
            return None, None

def main():
    """Main execution function with daily scraping features."""
    root = tk.Tk()
    root.withdraw()
    
    print("=" * 50)
    print("DAILY DUE AMOUNT SCRAPER")
    print("=" * 50)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print()
    
    # Step 1: User selects Excel file
    print("Please select the Excel file to upload...")
    excel_file = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx;*.xls")]
    )
    
    if not excel_file:
        print("No file selected. Exiting.")
        return

    # Step 2: Extract links and save to links.txt
    try:
        df = pd.read_excel(excel_file)
        if 'link' in df.columns:
            links = df['link'].tolist()
            with open('links.txt', 'w') as f:
                for link in links:
                    f.write(f"{link}\n")
            print(f"✓ Links extracted successfully from {excel_file}")
            print(f"✓ {len(links)} links saved to links.txt")
        else:
            print("Error: 'link' column not found in the Excel file.")
            return
    except Exception as e:
        print(f"An error occurred while reading Excel: {e}")
        return

    # Step 3: Run daily scraping
    print("\nStarting daily scraping process...")
    scraper = DailyDueScraper(headless=True)
    
    try:
        df_excel, report_df = scraper.process_links_daily(
            input_file='links.txt', 
            excel_file=excel_file, 
            max_workers=10
        )
        
        if df_excel is not None:
            print("\n" + "=" * 50)
            print("DAILY SCRAPING SUMMARY")
            print("=" * 50)
            
            # Count successful extractions
            success_count = len([val for val in df_excel['Due Amount'] if val and val != 'Not found' and not str(val).startswith('Error')])
            total_count = len(df_excel)
            
            print(f"Total URLs processed: {total_count}")
            print(f"Successful extractions: {success_count}")
            print(f"Success rate: {(success_count/total_count)*100:.1f}%")
            
            if report_df is not None:
                changes = len(report_df[report_df['Status'] == 'Changed'])
                print(f"Changes detected from previous day: {changes}")
            
            print(f"\nResults updated in: {excel_file}")
            print("Daily report and archive available in 'archive/' folder")
            print(f"Log file: scraping_{datetime.now().strftime('%Y%m%d')}.log")
            
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return

if __name__ == "__main__":
    main()
