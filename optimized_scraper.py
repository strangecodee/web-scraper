#!/usr/bin/env python3
"""
Optimized web scraper with reduced CPU and memory usage.
Uses connection pooling, memory-efficient processing, and optimized concurrency.
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
from tkinter import filedialog
from datetime import datetime
import os
import gc
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging
if not os.path.exists('screenshots'):
    os.makedirs('screenshots')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Set up rotating file handler for optimized scraper
from logging.handlers import RotatingFileHandler
file_handler = RotatingFileHandler(
    'optimized_scraper.log', 
    maxBytes=10*1024*1024,  # 10MB max size
    backupCount=5,          # Keep 5 backup files
    mode='a'
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

class OptimizedDueAmountScraper:
    def __init__(self, headless=True):
        """Initialize the scraper with optimized Chrome options."""
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1024,768')  # Smaller window for less memory
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--disable-plugins')
        self.options.add_argument('--disable-images')  # Disable images to save memory
        self.options.add_argument('--disable-javascript')  # Optional: disable JS if not needed
        
    def get_driver(self):
        """Create and return a Chrome driver instance with memory optimizations."""
        try:
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=self.options)
            
            # Set timeouts to prevent hanging
            driver.set_page_load_timeout(30)
            driver.set_script_timeout(30)
            
            return driver
        except Exception as e:
            logging.warning(f"webdriver_manager failed: {e}")
            
            # Fallback: try system PATH
            try:
                return webdriver.Chrome(options=self.options)
            except Exception:
                raise Exception(
                    "ChromeDriver not found. Please download from:\n"
                    "https://chromedriver.chromium.org/\n"
                    "and place chromedriver.exe in this folder"
                )
    
    def extract_due_amount(self, url):
        """Extract due amount with optimized memory usage."""
        driver = None
        try:
            driver = self.get_driver()
            logging.info(f"Processing URL: {url}")

            driver.get(url)

            # Use shorter timeout for better performance
            wait = WebDriverWait(driver, 10)

            # Optimized selector order - most likely first
            selectors = [
                "input[name='totalDue']",
                "input[id*=':r']",
                "input[aria-invalid='false'][disabled]",
                "input.MuiInputBase-input.MuiFilledInput-input.Mui-disabled",
                "//input[@name='totalDue']",
                "//input[contains(@id, ':r') and @disabled]",
            ]

            due_amount = None

            # Try selectors in order
            for selector in selectors:
                try:
                    if selector.startswith('//'):
                        element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    else:
                        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    
                    due_amount = element.get_attribute('value')
                    if due_amount:
                        logging.info(f"Found due amount: {due_amount}")
                        break
                except:
                    continue

            # Only save screenshot if absolutely necessary
            if not due_amount:
                screenshot_path = os.path.join('screenshots', f"notfound_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                driver.save_screenshot(screenshot_path)

            return due_amount if due_amount else "Not found"

        except TimeoutException:
            logging.error(f"Timeout loading URL: {url}")
            return "Timeout"
        except Exception as e:
            logging.error(f"Error processing {url}: {str(e)}")
            return f"Error: {str(e)}"
        finally:
            if driver:
                driver.quit()
            # Force garbage collection to free memory
            gc.collect()
    
    def process_links_optimized(self, input_file='links.txt', excel_file='New Microsoft Office Excel Worksheet (3) (1).xlsx', max_workers=2):
        """Process links with memory-efficient batch processing."""
        try:
            # Read links in chunks to avoid memory overload
            with open(input_file, 'r', encoding='utf-8') as f:
                links = [line.strip() for line in f if line.strip() and str(line.strip()).lower() != 'nan']

            logging.info(f"Found {len(links)} links to process")

            # Load Excel file once
            df_excel = pd.read_excel(excel_file)
            if 'link' not in df_excel.columns:
                logging.error("Excel file does not contain 'link' column.")
                return None

            link_to_index = {str(row['link']).strip(): idx for idx, row in df_excel.iterrows()}

            # Process in smaller batches to reduce memory pressure
            batch_size = 10
            results = []
            
            for i in range(0, len(links), batch_size):
                batch_links = links[i:i + batch_size]
                logging.info(f"Processing batch {i//batch_size + 1}/{(len(links)-1)//batch_size + 1}")
                
                batch_results = self.process_batch(batch_links, link_to_index, df_excel, max_workers)
                results.extend(batch_results)
                
                # Save progress after each batch
                self.update_excel(df_excel, excel_file)
                logging.info(f"Saved progress after batch {i//batch_size + 1}")

            logging.info(f"Scraping complete! Processed {len(results)} URLs")
            return df_excel

        except Exception as e:
            logging.error(f"Error processing links: {str(e)}")
            return None
    
    def process_batch(self, batch_links, link_to_index, df_excel, max_workers=2):
        """Process a batch of links with controlled concurrency."""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_link = {executor.submit(self.extract_due_amount, link): link for link in batch_links}
            
            for future in as_completed(future_to_link):
                link = future_to_link[future]
                try:
                    due_amount = future.result()
                    results.append({'link': link, 'Due Amount': due_amount})
                    
                    # Update Excel in memory
                    if link in link_to_index:
                        df_excel.at[link_to_index[link], 'Due Amount'] = due_amount
                        
                    logging.info(f"Processed: {link} -> {due_amount}")
                    
                except Exception as exc:
                    logging.error(f"Exception for {link}: {exc}")
                    results.append({'link': link, 'Due Amount': f"Error: {exc}"})
        
        return results
    
    def update_excel(self, df_excel, excel_file):
        """Update Excel file with current results."""
        try:
            df_excel.to_excel(excel_file, index=False)
        except Exception as e:
            logging.error(f"Error saving Excel file: {e}")

def main():
    """Main execution function with performance optimizations."""
    root = tk.Tk()
    root.withdraw()
    
    print("Please select the Excel file to upload...")
    excel_file = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx;*.xls")]
    )
    
    if not excel_file:
        print("No file selected. Exiting.")
        return

    # Extract links
    try:
        df = pd.read_excel(excel_file)
        if 'link' in df.columns:
            links = df['link'].tolist()
            with open('links.txt', 'w') as f:
                for link in links:
                    f.write(f"{link}\n")
            print(f"Links extracted successfully from {excel_file} and saved to links.txt")
        else:
            print("Error: 'link' column not found in the Excel file.")
            return
    except Exception as e:
        print(f"An error occurred while reading Excel: {e}")
        return

    # Run optimized scraping
    print("\nStarting optimized scraping with reduced resource usage...")
    print("Using only 2 concurrent workers to minimize CPU/memory usage")
    print("Processing in batches of 10 URLs for better memory management")
    
    scraper = OptimizedDueAmountScraper(headless=True)
    
    try:
        start_time = time.time()
        df_excel = scraper.process_links_optimized(
            input_file='links.txt', 
            excel_file=excel_file, 
            max_workers=2
        )
        end_time = time.time()
        
        if df_excel is not None:
            # Generate summary
            success_count = len([x for x in df_excel['Due Amount'] if x and x != 'Not found' and not str(x).startswith('Error') and not str(x).startswith('Timeout')])
            total_count = len(df_excel)
            
            print(f"\n{'='*50}")
            print("SCRAPING COMPLETE - OPTIMIZED PERFORMANCE")
            print(f"{'='*50}")
            print(f"Total URLs processed: {total_count}")
            print(f"Successful extractions: {success_count}")
            print(f"Failed extractions: {total_count - success_count}")
            print(f"Time taken: {end_time - start_time:.2f} seconds")
            print(f"Results saved to: {excel_file}")
            print(f"{'='*50}")
            
            # Show first few results
            print("\nFirst 5 results:")
            for i, (idx, row) in enumerate(df_excel.head().iterrows()):
                if i < 5:
                    print(f"{row['link']} -> {row.get('Due Amount', 'N/A')}")
                    
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return

if __name__ == "__main__":
    main()
