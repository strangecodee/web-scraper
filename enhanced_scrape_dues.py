import os
import time
import logging
import requests
import zipfile
import subprocess
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from tkinter import Tk, filedialog, messagebox

# Simplified logging config
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler()
    ]
)

class DueAmountScraper:
    def __init__(self, headless=True):
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

    def get_installed_chrome_version(self):
        try:
            output = subprocess.check_output(
                r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
                shell=True
            ).decode(errors='ignore')
            version = output.strip().split()[-1]
            logging.info(f"Detected Chrome version: {version}")
            return version
        except Exception as e:
            logging.error(f"Failed to detect Chrome version: {e}")
            return None

    def download_chromedriver(self, chrome_version):
        platform = "win64"
        url = f"https://storage.googleapis.com/chrome-for-testing-public/{chrome_version}/{platform}/chromedriver-{platform}.zip"
        logging.info(f"Downloading ChromeDriver from: {url}")

        driver_dir = os.path.abspath("drivers")
        zip_path = os.path.join(driver_dir, "chromedriver.zip")
        extract_path = os.path.join(driver_dir, "chromedriver")

        os.makedirs(extract_path, exist_ok=True)

        try:
            r = requests.get(url, stream=True)
            if r.status_code != 200:
                raise Exception(f"ChromeDriver not found at {url}")

            with open(zip_path, 'wb') as f:
                f.write(r.content)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            driver_path = os.path.join(extract_path, "chromedriver-win64", "chromedriver.exe")
            if not os.path.exists(driver_path):
                logging.error("ChromeDriver executable not found after extraction.")
                return None
            else:
                logging.info(f"ChromeDriver downloaded and extracted to: {driver_path}")
                return driver_path

        except Exception as e:
            logging.error(f"Error downloading ChromeDriver: {e}")
            return None

    def get_driver(self):
        chrome_version = self.get_installed_chrome_version()
        if not chrome_version:
            raise Exception("Could not detect Chrome version.")

        driver_path = self.download_chromedriver(chrome_version)
        if not driver_path or not os.path.exists(driver_path):
            raise Exception("ChromeDriver download failed or path invalid.")

        return webdriver.Chrome(service=Service(driver_path), options=self.options)

    def extract_due_amount(self, url):
        driver = None
        try:
            driver = self.get_driver()
            logging.info(f"Processing URL: {url}")
            driver.get(url)
            wait = WebDriverWait(driver, 15)

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

            for selector in selectors[:5]:
                try:
                    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    due_amount = element.get_attribute('value')
                    if due_amount:
                        logging.info(f"Found due amount via CSS: {due_amount}")
                        break
                except:
                    continue

            if not due_amount:
                for xpath in selectors[5:]:
                    try:
                        element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                        due_amount = element.get_attribute('value')
                        if due_amount:
                            logging.info(f"Found due amount via XPath: {due_amount}")
                            break
                    except:
                        continue

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

            if not due_amount:
                screenshot_path = f"screenshots/failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                os.makedirs("screenshots", exist_ok=True)
                driver.save_screenshot(screenshot_path)
                logging.info(f"Saved failure screenshot: {screenshot_path}")

            return due_amount if due_amount else "Not found"

        except TimeoutException:
            logging.error(f"Timeout while processing URL: {url}")
            if driver:
                screenshot_path = f"screenshots/timeout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                os.makedirs("screenshots", exist_ok=True)
                driver.save_screenshot(screenshot_path)
                logging.info(f"Saved timeout screenshot: {screenshot_path}")
            return "Error: Timeout"

        except Exception as e:
            logging.error(f"Error processing URL {url}: {str(e)}")
            if driver:
                screenshot_path = f"screenshots/error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                os.makedirs("screenshots", exist_ok=True)
                driver.save_screenshot(screenshot_path)
                logging.info(f"Saved error screenshot: {screenshot_path}")
            return f"Error: {str(e)}"

        finally:
            if driver:
                driver.quit()

    def process_links(self, input_file=None, sheet_name='Sheet2'):
        try:
            if input_file is None:
                print("📂 Please select your Excel file with the 'link' column...")
                root = Tk()
                root.withdraw()
                input_file = filedialog.askopenfilename(
                    title="Select Excel File",
                    filetypes=[("Excel files", "*.xlsx *.xls")]
                )
                root.destroy()
                if not input_file:
                    print("❌ No file selected. Exiting.")
                    return None

            df = pd.read_excel(input_file, sheet_name=sheet_name)

            if 'link' not in df.columns:
                logging.error("Excel file must contain a column named 'link'")
                return None

            logging.info(f"Found {len(df)} links to process")

            os.makedirs("screenshots", exist_ok=True)

            for idx, row in df.iterrows():
                url = row['link']
                due_amount = self.extract_due_amount(url)

                status = 'Success' if due_amount and due_amount != 'Not found' and not due_amount.startswith('Error') else 'Failed'
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                df.at[idx, 'Due Amount'] = due_amount
                df.at[idx, 'Status'] = status
                df.at[idx, 'Timestamp'] = timestamp

                # Log progress every 10 or at last row
                if (idx + 1) % 10 == 0 or idx == len(df) - 1:
                    logging.info(f"Processed {idx + 1}/{len(df)} URLs")

                time.sleep(2)

            df.to_excel(input_file, sheet_name=sheet_name, index=False)
            logging.info(f"✅ Updated Excel saved to {input_file}")

            return df

        except FileNotFoundError:
            logging.error(f"File not found: {input_file}")
            return None
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            return None

def main():
    print("🔄 Starting Due Amount Scraper...\n")
    scraper = DueAmountScraper(headless=True)

    results = scraper.process_links()

    if results is not None:
        total = len(results)
        success = len(results[results['Status'] == 'Success'])
        failed = total - success

        print("\n📊 Scraping Summary:")
        print(f"🔗 Total URLs processed : {total}")
        print(f"✅ Successful extractions: {success}")
        print(f"❌ Failed extractions    : {failed}")

        print("\n📋 First 5 results:")
        print(results[['URL', 'Due Amount', 'Status']].head(5).to_string(index=False))

        if failed > 0:
            print("\n🖼️  Check screenshots folder for failed cases.")

        # Show popup summary
        root = Tk()
        root.withdraw()
        messagebox.showinfo(
            "Scraping Completed",
            f"Total URLs processed: {total}\n"
            f"Successful extractions: {success}\n"
            f"Failed extractions: {failed}\n\n"
            f"Results saved to your Excel file."
        )
        root.destroy()

if __name__ == "__main__":
    main()
