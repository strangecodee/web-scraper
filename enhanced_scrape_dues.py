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
    
    def process_links(self, input_file='links.txt', output_file='due_amounts_enhanced.xlsx'):
        """Process all links from the input file."""
        try:
            # Read links from file
            with open(input_file, 'r', encoding='utf-8') as f:
                links = [line.strip() for line in f if line.strip() and str(line.strip()).lower() != 'nan']
            
            logging.info(f"Found {len(links)} valid links to process")
            
            results = []
            failed_links = []
            
            for idx, link in enumerate(links, 1):
                logging.info(f"Processing {idx}/{len(links)}: {link}")
                
                due_amount = self.extract_due_amount(link)
                
                result = {
                    'URL': link,
                    'Due Amount': due_amount,
                    'Status': 'Success' if due_amount and due_amount != 'Not found' and not due_amount.startswith('Error') else 'Failed',
                    'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                results.append(result)
                
                if result['Status'] == 'Failed':
                    failed_links.append(link)
                
                # Add delay between requests
                time.sleep(2)
            
            # Create DataFrame and save results
            df = pd.DataFrame(results)
            
            # Save to Excel with formatting
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Due Amounts', index=False)
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Due Amounts']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            logging.info(f"Scraping complete! Results saved to {output_file}")
            logging.info(f"Total processed: {len(results)}")
            logging.info(f"Successful: {len([r for r in results if r['Status'] == 'Success'])}")
            logging.info(f"Failed: {len(failed_links)}")
            
            if failed_links:
                logging.info(f"Failed links: {failed_links}")
            
            return df
            
        except FileNotFoundError:
            logging.error(f"Input file {input_file} not found")
            return None
        except Exception as e:
            logging.error(f"Error processing links: {str(e)}")
            return None

def main():
    """Main execution function."""
    scraper = DueAmountScraper(headless=True)
    results = scraper.process_links()
    
    if results is not None:
        print("\nScraping Summary:")
        print(f"Total URLs processed: {len(results)}")
        print(f"Successful extractions: {len(results[results['Status'] == 'Success'])}")
        print(f"Failed extractions: {len(results[results['Status'] == 'Failed'])}")
        print("\nFirst 10 results:")
        print(results.head(10))

if __name__ == "__main__":
    main()
