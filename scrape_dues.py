import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_due_amount(url):
    """Visits a URL and extracts the total due amount."""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        time.sleep(5)  # Wait for the page to load

        # This is a placeholder selector. We will need to inspect the actual page
        # to find the correct selector for the "total due amount".
        due_amount_element = driver.find_element(By.XPATH, '//*[contains(text(), "Total Due")]/following-sibling::div')
        due_amount = due_amount_element.text
        
        driver.quit()
        return due_amount
    except Exception as e:
        print(f"Error processing {url}: {e}")
        if driver:
            driver.quit()
        return "Error"

def main():
    """Reads links from a file, scrapes data, and saves to a new Excel file."""
    try:
        with open('links.txt', 'r') as f:
            links = [line.strip() for line in f if line.strip() and line.strip() != 'nan']

        results = []
        for link in links:
            print(f"Processing {link}...")
            due_amount = get_due_amount(link)
            results.append({'Link': link, 'Total Due Amount': due_amount})

        # Create a new DataFrame with the results
        results_df = pd.DataFrame(results)

        # Save the results to a new Excel file
        results_df.to_excel('due_amounts.xlsx', index=False)
        print("Scraping complete. Results saved to due_amounts.xlsx")

    except FileNotFoundError:
        print("Error: links.txt not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
