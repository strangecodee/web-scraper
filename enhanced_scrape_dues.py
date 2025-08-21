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
import threading
import tempfile

# Set up logging
import os
if not os.path.exists('screenshots'):
    os.makedirs('screenshots')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Separate loggers for success and error
success_logger = logging.getLogger('success_logger')
success_handler = logging.FileHandler('success.log')
success_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
success_logger.addHandler(success_handler)
success_logger.setLevel(logging.INFO)

error_logger = logging.getLogger('error_logger')
error_handler = logging.FileHandler('error.log')
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
error_logger.addHandler(error_handler)
error_logger.setLevel(logging.INFO)

class DueAmountScraper:
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

        # Create a unique user data directory
        self.options.add_argument(f"user-data-dir={tempfile.mkdtemp()}")
        
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
                "input[id*=':r']",  # Matches IDs like :r4:, :r5:, etc.
                "input[aria-invalid='false'][disabled]",
                "input.MuiInputBase-input.MuiFilledInput-input.Mui-disabled",
                "input[value*='8051']",  # If we know the value
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
    
    def process_links(self, input_file='links.txt', excel_file='New Microsoft Office Excel Worksheet (3) (1).xlsx', max_workers=5, realtime=False):
        """Process all links from the input file using multithreading and update the given Excel file with due amounts.
        If realtime=True, prints progress for each link as soon as it's processed.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                links = [line.strip() for line in f if line.strip() and str(line.strip()).lower() != 'nan']

            logging.info(f"Found {len(links)} valid links to process")

            df_excel = pd.read_excel(excel_file)
            if 'link' not in df_excel.columns:
                logging.error(f"Excel file does not contain 'link' column.")
                print("Error: Excel file does not contain 'link' column.")
                return None

            if 'Due Amount' not in df_excel.columns:
                df_excel['Due Amount'] = None

            link_to_index = {str(row['link']).strip(): idx for idx, row in df_excel.iterrows()}

            results = []
            failed_links = []
            print_lock = threading.Lock()

            def scrape_link(link):
                due_amount = self.extract_due_amount(link)
                status = 'Success' if due_amount and due_amount != 'Not found' and not str(due_amount).startswith('Error') else 'Failed'
                result = {
                    'link': link,
                    'Due Amount': due_amount,
                    'Status': status,
                    'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                if realtime:
                    with print_lock:
                        print(f"[{result['Timestamp']}] {link} => {due_amount} ({status})")
                return result

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_link = {executor.submit(scrape_link, link): link for link in links}
                for idx, future in enumerate(as_completed(future_to_link), 1):
                    link = future_to_link[future]
                    try:
                        result = future.result()
                        results.append(result)
                        logging.info(f"Processed {idx}/{len(links)}: {link}")
                        if link in link_to_index:
                            df_excel.at[link_to_index[link], 'Due Amount'] = result['Due Amount']
                            # Save after each update for real-time monitoring
                            df_excel.to_excel(excel_file, index=False)
                        if result['Status'] == 'Success':
                            success_logger.info(f"{link} | Due Amount: {result['Due Amount']}")
                        else:
                            error_logger.info(f"{link} | Due Amount: {result['Due Amount']}")
                            failed_links.append(link)
                    except Exception as exc:
                        logging.error(f"Exception for {link}: {exc}")
                        error_logger.info(f"{link} | Exception: {exc}")
                        failed_links.append(link)

            # Save updated Excel file (overwrite, not append)
            df_excel.to_excel(excel_file, index=False)

            logging.info(f"Scraping complete! Results updated in {excel_file}")
            logging.info(f"Total processed: {len(results)}")
            logging.info(f"Successful: {len([r for r in results if r['Status'] == 'Success'])}")
            logging.info(f"Failed: {len(failed_links)}")

            if failed_links:
                logging.info(f"Failed links: {failed_links}")

            return df_excel

        except FileNotFoundError:
            logging.error(f"Input file {input_file} or Excel file {excel_file} not found")
            print(f"Error: Input file {input_file} or Excel file {excel_file} not found")
            return None
        except Exception as e:
            logging.error(f"Error processing links: {str(e)}")
            print(f"Error processing links: {str(e)}")
            return None

def main():
    """Main execution function."""
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

    scraper = DueAmountScraper(headless=True)
    df_excel = None
    summary_results = None
    try:
        print("Starting scraping (real-time output below)...")
        df_excel = scraper.process_links(input_file='links.txt', excel_file=excel_file, max_workers=10, realtime=True)
        with open('links.txt', 'r') as f:
            links = [line.strip() for line in f if line.strip() and str(line.strip()).lower() != 'nan']
        summary_results = []
        for link in links:
            due_amount = df_excel.loc[df_excel['link'] == link, 'Due Amount'].values[0] if 'Due Amount' in df_excel.columns and link in df_excel['link'].values else None
            status = 'Success' if due_amount and due_amount != 'Not found' and not str(due_amount).startswith('Error') else 'Failed'
            summary_results.append({'link': link, 'Due Amount': due_amount, 'Status': status})

        # --- Save with new filename including date and day ---
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        day_str = now.strftime("%A")
        base, ext = os.path.splitext(excel_file)
        default_name = f"{os.path.basename(base)}_{date_str}_{day_str}{ext}"

        print("\nChoose where to save the updated Excel file...")
        save_path = filedialog.asksaveasfilename(
            title="Save Updated Excel File",
            initialfile=default_name,
            defaultextension=ext,
            filetypes=[("Excel files", "*.xlsx;*.xls")]
        )
        if save_path:
            df_excel.to_excel(save_path, index=False)
            print(f"\nResults saved to: {save_path}")
        else:
            print("No save location selected. File not saved.")

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return

    if df_excel is not None and summary_results is not None:
        print("\nScraping Summary:")
        print(f"Total URLs processed: {len(summary_results)}")
        print(f"Successful extractions: {len([r for r in summary_results if r['Status'] == 'Success'])}")
        print(f"Failed extractions: {len([r for r in summary_results if r['Status'] == 'Failed'])}")
        print("\nFirst 10 results:")
        for r in summary_results[:10]:
            print(r)

if __name__ == "__main__":
    main()
