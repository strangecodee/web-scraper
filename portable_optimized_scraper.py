#!/usr/bin/env python3
"""
Portable Optimized Web Scraper - All-in-one version for new PCs.
This is a self-contained version that includes everything needed.
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
from datetime import datetime
import os
import gc
from concurrent.futures import ThreadPoolExecutor, as_completed
from logging.handlers import RotatingFileHandler

class PortableOptimizedScraper:
    def __init__(self, headless=True):
        """Initialize the portable scraper with all optimizations."""
        self.setup_logging()
        self.setup_directories()
        
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1024,768')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--disable-plugins')
        self.options.add_argument('--disable-images')
        
    def setup_logging(self):
        """Set up logging with rotation."""
        if not hasattr(self, 'logging_setup'):
            os.makedirs('logs', exist_ok=True)
            
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            
            # Rotating file handler
            file_handler = RotatingFileHandler(
                os.path.join('logs', 'optimized_scraper.log'),
                maxBytes=10*1024*1024,
                backupCount=5,
                mode='a'
            )
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logging.getLogger().addHandler(file_handler)
            
            self.logging_setup = True
    
    def setup_directories(self):
        """Create necessary directories."""
        os.makedirs('screenshots', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        os.makedirs('data', exist_ok=True)
    
    def get_driver(self):
        """Create Chrome driver with enhanced error handling."""
        try:
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=self.options)
            
            driver.set_page_load_timeout(30)
            driver.set_script_timeout(30)
            
            return driver
        except Exception as e:
            logging.error(f"ChromeDriver setup failed: {e}")
            
            # Try fallback methods
            try:
                return webdriver.Chrome(options=self.options)
            except Exception:
                self.show_error_dialog(
                    "ChromeDriver Not Found",
                    "Please install ChromeDriver:\n"
                    "1. Download from https://chromedriver.chromium.org/\n"
                    "2. Place chromedriver.exe in this folder\n"
                    "3. Restart the application"
                )
                raise
    
    def show_error_dialog(self, title, message):
        """Show error dialog for user-friendly messages."""
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
        root.destroy()
    
    def show_info_dialog(self, title, message):
        """Show information dialog."""
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(title, message)
        root.destroy()
    
    def extract_due_amount(self, url):
        """Extract due amount with optimized memory usage."""
        driver = None
        try:
            driver = self.get_driver()
            logging.info(f"Processing URL: {url}")

            driver.get(url)

            # Use shorter timeout for better performance
            wait = WebDriverWait(driver, 10)

            # Optimized selector order
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

            # Only save screenshot if not found
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
            gc.collect()
    
    def process_links_optimized(self, input_file='links.txt', excel_file=None, max_workers=2):
        """Process links with memory-efficient batch processing."""
        try:
            # Read links
            if not os.path.exists(input_file):
                with open(input_file, 'w') as f:
                    f.write("# Add your URLs here, one per line\n")
                
            with open(input_file, 'r', encoding='utf-8') as f:
                links = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

            if not links:
                self.show_info_dialog("No URLs", "Please add URLs to links.txt file")
                return None

            logging.info(f"Found {len(links)} links to process")

            # If no Excel file provided, create one
            if not excel_file:
                excel_file = os.path.join('data', 'scraping_results.xlsx')
                df_excel = pd.DataFrame({'link': links, 'Due Amount': [''] * len(links)})
                df_excel.to_excel(excel_file, index=False)
            else:
                df_excel = pd.read_excel(excel_file)
                if 'link' not in df_excel.columns:
                    logging.error("Excel file does not contain 'link' column.")
                    return None

            link_to_index = {str(row['link']).strip(): idx for idx, row in df_excel.iterrows()}

            # Process in batches
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
            self.show_error_dialog("Processing Error", f"An error occurred: {str(e)}")
            return None
    
    def process_batch(self, batch_links, link_to_index, df_excel, max_workers=2):
        """Process a batch of links."""
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
        """Update Excel file."""
        try:
            df_excel.to_excel(excel_file, index=False)
        except Exception as e:
            logging.error(f"Error saving Excel file: {e}")
    
    def run(self):
        """Main execution method."""
        root = tk.Tk()
        root.withdraw()
        
        print("🚀 Portable Optimized Web Scraper")
        print("=" * 50)
        
        # Ask for Excel file or create new
        use_existing = messagebox.askyesno(
            "Excel File", 
            "Do you have an existing Excel file with URLs?\n\n"
            "Yes: Select existing file\n"
            "No: Create new file from links.txt"
        )
        
        excel_file = None
        if use_existing:
            excel_file = filedialog.askopenfilename(
                title="Select Excel File",
                filetypes=[("Excel files", "*.xlsx;*.xls")]
            )
            if not excel_file:
                print("No file selected. Exiting.")
                return
        
        print("\nStarting optimized scraping with reduced resource usage...")
        print("Using only 2 concurrent workers to minimize CPU/memory usage")
        print("Processing in batches of 10 URLs for better memory management")
        
        try:
            start_time = time.time()
            df_excel = self.process_links_optimized(
                input_file='links.txt', 
                excel_file=excel_file, 
                max_workers=2
            )
            end_time = time.time()
            
            if df_excel is not None:
                success_count = len([x for x in df_excel['Due Amount'] if x and x != 'Not found' and not str(x).startswith('Error') and not str(x).startswith('Timeout')])
                total_count = len(df_excel)
                
                print(f"\n{'='*50}")
                print("SCRAPING COMPLETE - PORTABLE OPTIMIZED VERSION")
                print(f"{'='*50}")
                print(f"Total URLs processed: {total_count}")
                print(f"Successful extractions: {success_count}")
                print(f"Failed extractions: {total_count - success_count}")
                print(f"Time taken: {end_time - start_time:.2f} seconds")
                
                result_file = excel_file if excel_file else 'data/scraping_results.xlsx'
                print(f"Results saved to: {result_file}")
                print(f"{'='*50}")
                
                self.show_info_dialog(
                    "Scraping Complete",
                    f"Processed {total_count} URLs\n"
                    f"Successful: {success_count}\n"
                    f"Failed: {total_count - success_count}\n"
                    f"Time: {end_time - start_time:.2f} seconds\n"
                    f"Results saved to: {os.path.basename(result_file)}"
                )
                    
        except Exception as e:
            print(f"An error occurred during scraping: {e}")
            self.show_error_dialog("Scraping Error", f"An error occurred: {str(e)}")
            return

def main():
    """Main function for portable scraper."""
    print("Setting up portable optimized scraper...")
    scraper = PortableOptimizedScraper(headless=True)
    scraper.run()

if __name__ == "__main__":
    main()
