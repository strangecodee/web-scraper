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
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler()
    ]
)

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
        
    def get_driver(self):
        """Create and return a Chrome driver instance."""
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )
    
    def extract_due_amount(self, url):
        """Extract due amount from the specific input field."""
        driver = None
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
            
            # Take screenshot for debugging
            driver.save_screenshot(f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
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
    
    def process_links(self, input_file='links.txt', excel_file='New Microsoft Office Excel Worksheet (3) (1).xlsx', max_workers=5):
        """Process all links from the input file using multithreading and update the given Excel file with due amounts."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        try:
            # Read links from file
            with open(input_file, 'r', encoding='utf-8') as f:
                links = [line.strip() for line in f if line.strip() and str(line.strip()).lower() != 'nan']

            logging.info(f"Found {len(links)} valid links to process")

            # Load the Excel file
            df_excel = pd.read_excel(excel_file)
            if 'link' not in df_excel.columns:
                logging.error(f"Excel file does not contain 'link' column.")
                return None

            # Prepare a mapping from link to index for fast update
            link_to_index = {str(row['link']).strip(): idx for idx, row in df_excel.iterrows()}

            # Results for logging
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
                        if result['Status'] == 'Failed':
                            failed_links.append(link)
                    except Exception as exc:
                        logging.error(f"Exception for {link}: {exc}")
                        failed_links.append(link)

            # Save updated Excel file
            with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                df_excel.to_excel(writer, index=False)

            logging.info(f"Scraping complete! Results updated in {excel_file}")
            logging.info(f"Total processed: {len(results)}")
            logging.info(f"Successful: {len([r for r in results if r['Status'] == 'Success'])}")
            logging.info(f"Failed: {len(failed_links)}")

            if failed_links:
                logging.info(f"Failed links: {failed_links}")

            return df_excel

        except FileNotFoundError:
            logging.error(f"Input file {input_file} or Excel file {excel_file} not found")
            return None
        except Exception as e:
            logging.error(f"Error processing links: {str(e)}")
            return None

def main():
    """Main execution function."""
    scraper = DueAmountScraper(headless=True)
    results = scraper.process_links(max_workers=10)
    
    if results is not None:
        print("\nScraping Summary:")
        print(f"Total URLs processed: {len(results)}")
        print(f"Successful extractions: {len(results[results['Status'] == 'Success'])}")
        print(f"Failed extractions: {len(results[results['Status'] == 'Failed'])}")
        print("\nFirst 10 results:")
        print(results.head(10))

if __name__ == "__main__":
    main()
