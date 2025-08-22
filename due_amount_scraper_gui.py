import os
import time
import threading
import logging
import subprocess
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from tkinter import Tk, filedialog, messagebox, Button, Label, Text, Scrollbar, END, DISABLED, NORMAL, StringVar, Frame, IntVar, Checkbutton
from tkinter import ttk
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

# ========== DueAmountScraper class ==========

class DueAmountScraper:
    def __init__(self, headless=True):
        self.options = webdriver.ChromeOptions()
        if headless:
            # Use modern headless mode
            self.options.add_argument('--headless=new')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--disable-plugins')
        self.options.add_argument('--disable-images')
        self.options.add_argument('--disable-javascript')
        self.options.add_argument('--disable-css')
        self.options.add_argument('--disable-web-security')
        self.options.add_argument('--disable-features=VizDisplayCompositor')
        self.options.add_argument('--disable-background-timer-throttling')
        self.options.add_argument('--disable-backgrounding-occluded-windows')
        self.options.add_argument('--disable-renderer-backgrounding')
        self.options.add_argument('--disable-features=TranslateUI')
        self.options.add_argument('--disable-ipc-flooding-protection')
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--memory-pressure-off')
        self.options.add_argument('--max_old_space_size=4096')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_experimental_option("prefs", {
            "profile.default_content_setting_values": {
                "images": 2,
                "plugins": 2,
                "popups": 2,
                "geolocation": 2,
                "notifications": 2,
                "media_stream": 2,
            },
            "profile.managed_default_content_settings": {
                "images": 2
            },
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.cookies": 1,
            "profile.managed_default_content_settings.javascript": 1,
            "profile.managed_default_content_settings.plugins": 1,
            "profile.managed_default_content_settings.popups": 2,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.managed_default_content_settings.media_stream": 2,
        })

    def get_driver(self):
        # Selenium Manager will download/resolve the matching driver automatically
        return webdriver.Chrome(options=self.options)

    def extract_due_amount(self, url):
        driver = None
        try:
            driver = self.get_driver()
            driver.get(url)
            wait = WebDriverWait(driver, 5)  # Ultra-fast timeout

            # Optimized selectors - most common first
            selectors = [
                "input[name='totalDue']",
                "input[disabled][value]",
                "input[aria-invalid='false'][disabled]",
                "input.MuiInputBase-input.MuiFilledInput-input.Mui-disabled",
                "input[value*='8051']",
                "//input[@name='totalDue']",
                "//input[contains(@id, ':r') and @disabled]",
                "//input[@aria-invalid='false' and @disabled]"
            ]

            due_amount = None

            # Try CSS selectors first (faster)
            for selector in selectors[:5]:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    due_amount = element.get_attribute('value')
                    if due_amount and due_amount.strip():
                        return due_amount.strip()
                except:
                    continue

            # Try XPath if CSS failed
            for xpath in selectors[5:]:
                try:
                    element = driver.find_element(By.XPATH, xpath)
                    due_amount = element.get_attribute('value')
                    if due_amount and due_amount.strip():
                        return due_amount.strip()
                except:
                    continue

            # Fast fallback - get all inputs and check values
            try:
                inputs = driver.find_elements(By.TAG_NAME, 'input')
                for input_elem in inputs:
                    value = input_elem.get_attribute('value')
                    if value and value.strip().isdigit() and len(value.strip()) > 0:
                        return value.strip()
            except:
                pass

            return "Not found"
            
        except TimeoutException:
            return "Error: Timeout"
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    def process_single_url(self, args):
        """Process a single URL - used for parallel processing"""
        idx, url = args
        try:
            due_amount = self.extract_due_amount(url)
            status = 'Success' if due_amount and due_amount != 'Not found' and not due_amount.startswith('Error') else 'Failed'
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return idx, due_amount, status, timestamp
        except Exception as e:
            return idx, f"Error: {str(e)}", 'Failed', datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def process_links(self, input_file=None, sheet_name=None, delay=0.1, progress_callback=None, stop_callback=None, max_workers=8):
        try:
            # If no sheet specified, use the first sheet
            if sheet_name is None:
                excel_file = pd.ExcelFile(input_file)
                sheet_name = excel_file.sheet_names[0]
                logging.info(f"Using first sheet: {sheet_name}")
            
            df = pd.read_excel(input_file, sheet_name=sheet_name)
            if 'link' not in df.columns:
                logging.error("Excel file must contain a column named 'link'")
                return None

            logging.info(f"Found {len(df)} links to process with {max_workers} parallel workers")

            # Prepare URLs for parallel processing
            urls_to_process = [(idx, row['link']) for idx, row in df.iterrows()]
            
            # Use ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_idx = {executor.submit(self.process_single_url, (idx, url)): idx 
                               for idx, url in urls_to_process}
                
                completed = 0
                for future in as_completed(future_to_idx):
                    if stop_callback and stop_callback():
                        logging.info("Scraping stopped by user")
                        break
                    
                    try:
                        idx, due_amount, status, timestamp = future.result()
                        df.at[idx, 'Due Amount'] = due_amount
                        df.at[idx, 'Status'] = status
                        df.at[idx, 'Timestamp'] = timestamp
                        
                        completed += 1
                        if progress_callback:
                            progress_callback(completed, len(df))
                            
                        logging.info(f"✅ Processed {completed}/{len(df)}: {due_amount}")
                        
                    except Exception as e:
                        completed += 1
                        logging.error(f"❌ Error processing URL: {str(e)}")
                        if progress_callback:
                            progress_callback(completed, len(df))

            df.to_excel(input_file, sheet_name=sheet_name, index=False)
            logging.info(f"Updated Excel saved to {input_file}")

            return df

        except FileNotFoundError:
            logging.error(f"File not found: {input_file}")
            return None
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            return None

# ========== Tkinter GUI ==========

class ScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WebMiner - Professional Web Scraping Tool")
        
        # Make window fullscreen and responsive
        self.root.state('zoomed')  # Maximize window
        self.root.configure(bg='#f0f0f0')
        
        # Configure style
        self.setup_styles()
        
        # Main container - responsive padding
        main_frame = Frame(root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Header
        header_frame = Frame(main_frame, bg='#2c3e50', height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title_label = Label(header_frame, text="WebMiner", 
                            font=("Arial", 24, "bold"), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        subtitle_label = Label(header_frame, text="Professional Web Scraping Tool", 
                               font=("Arial", 12), fg='#bdc3c7', bg='#2c3e50')
        subtitle_label.pack()
        
        # File selection section
        file_frame = Frame(main_frame, bg='white', relief='raised', bd=1)
        file_frame.pack(fill='x', pady=(0, 15))
        
        file_header = Label(file_frame, text="📁 File Selection", 
                           font=("Arial", 12, "bold"), bg='white', fg='#2c3e50')
        file_header.pack(anchor='w', padx=15, pady=(15, 10))
        
        file_button_frame = Frame(file_frame, bg='white')
        file_button_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        self.select_button = ttk.Button(file_button_frame, text="📂 Select Excel File", 
                                       command=self.select_file, style='Accent.TButton')
        self.select_button.pack(side='left')
        
        self.file_label = Label(file_button_frame, text="No file selected", 
                               fg="red", bg='white', font=("Arial", 9))
        self.file_label.pack(side='left', padx=(10, 0))
        
        # Sheet selection section
        sheet_frame = Frame(main_frame, bg='white', relief='raised', bd=1)
        sheet_frame.pack(fill='x', pady=(0, 15))
        
        sheet_header = Label(sheet_frame, text="📊 Sheet Selection", 
                            font=("Arial", 12, "bold"), bg='white', fg='#2c3e50')
        sheet_header.pack(anchor='w', padx=15, pady=(15, 10))
        
        sheet_content = Frame(sheet_frame, bg='white')
        sheet_content.pack(fill='x', padx=15, pady=(0, 15))
        
        sheet_label = Label(sheet_content, text="Available Sheets:", 
                           font=("Arial", 10), bg='white')
        sheet_label.pack(anchor='w')
        
        self.sheet_var = StringVar()
        self.sheet_combo = ttk.Combobox(sheet_content, textvariable=self.sheet_var, 
                                       state="readonly", width=40, font=("Arial", 10))
        self.sheet_combo.pack(anchor='w', pady=(5, 0))
        self.sheet_combo.bind('<<ComboboxSelected>>', self.on_sheet_selected)
        
        # Settings section
        settings_frame = Frame(main_frame, bg='white', relief='raised', bd=1)
        settings_frame.pack(fill='x', pady=(0, 15))
        
        settings_header = Label(settings_frame, text="⚙️ Settings", 
                               font=("Arial", 12, "bold"), bg='white', fg='#2c3e50')
        settings_header.pack(anchor='w', padx=15, pady=(15, 10))
        
        settings_content = Frame(settings_frame, bg='white')
        settings_content.pack(fill='x', padx=15, pady=(0, 15))
        
        # Headless mode option
        self.headless_var = IntVar(value=1)
        self.headless_check = Checkbutton(settings_content, text="Run in Headless Mode (Faster)", 
                                         variable=self.headless_var, bg='white', 
                                         font=("Arial", 10))
        self.headless_check.pack(anchor='w')
        
        # Thread count setting
        thread_frame = Frame(settings_content, bg='white')
        thread_frame.pack(anchor='w', pady=(10, 0))
        
        thread_label = Label(thread_frame, text="Number of parallel threads:", 
                            font=("Arial", 10), bg='white')
        thread_label.pack(side='left')
        
        self.thread_var = StringVar(value="8")
        thread_spinbox = ttk.Spinbox(thread_frame, from_=1, to=16, increment=1, 
                                    textvariable=self.thread_var, width=10)
        thread_spinbox.pack(side='left', padx=(10, 0))
        
        # Delay setting (minimal for parallel processing)
        delay_frame = Frame(settings_content, bg='white')
        delay_frame.pack(anchor='w', pady=(10, 0))
        
        delay_label = Label(delay_frame, text="Delay between requests (seconds):", 
                           font=("Arial", 10), bg='white')
        delay_label.pack(side='left')
        
        self.delay_var = StringVar(value="0.1")
        delay_spinbox = ttk.Spinbox(delay_frame, from_=0.0, to=1.0, increment=0.1, 
                                   textvariable=self.delay_var, width=10)
        delay_spinbox.pack(side='left', padx=(10, 0))
        
        # Progress section
        progress_frame = Frame(main_frame, bg='white', relief='raised', bd=1)
        progress_frame.pack(fill='x', pady=(0, 15))
        
        progress_header = Label(progress_frame, text="📈 Progress", 
                               font=("Arial", 12, "bold"), bg='white', fg='#2c3e50')
        progress_header.pack(anchor='w', padx=15, pady=(15, 10))
        
        progress_content = Frame(progress_frame, bg='white')
        progress_content.pack(fill='x', padx=15, pady=(0, 15))
        
        self.progress_var = StringVar(value="Ready to start")
        self.progress_label = Label(progress_content, textvariable=self.progress_var, 
                                   font=("Arial", 10), bg='white', fg='#27ae60')
        self.progress_label.pack(anchor='w')
        
        self.progress_bar = ttk.Progressbar(progress_content, mode='determinate')
        self.progress_bar.pack(fill='x', pady=(5, 0))
        
        # Control buttons
        button_frame = Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=(0, 15))
        
        self.start_button = ttk.Button(button_frame, text="🚀 Start Scraping", 
                                      command=self.start_scraping, state=DISABLED, 
                                      style='Accent.TButton')
        self.start_button.pack(side='left')
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Stop", 
                                     command=self.stop_scraping, state=DISABLED)
        self.stop_button.pack(side='left', padx=(10, 0))
        
        self.clear_button = ttk.Button(button_frame, text="🗑️ Clear Log", 
                                      command=self.clear_log)
        self.clear_button.pack(side='right')
        
        # Log section
        log_frame = Frame(main_frame, bg='white', relief='raised', bd=1)
        log_frame.pack(fill='both', expand=True)
        
        log_header = Label(log_frame, text="📝 Activity Log", 
                          font=("Arial", 12, "bold"), bg='white', fg='#2c3e50')
        log_header.pack(anchor='w', padx=15, pady=(15, 10))
        
        log_content = Frame(log_frame, bg='white')
        log_content.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Create text widget with scrollbar
        text_frame = Frame(log_content, bg='white')
        text_frame.pack(fill='both', expand=True)
        
        self.log_text = Text(text_frame, state=DISABLED, 
                            font=("Consolas", 10), bg='#2c3e50', fg='#ecf0f1')
        self.log_text.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, command=self.log_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Status bar
        status_frame = Frame(main_frame, bg='#34495e', height=25)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.status_var = StringVar(value="Ready")
        self.status_label = Label(status_frame, textvariable=self.status_var, 
                                 font=("Arial", 9), fg='white', bg='#34495e')
        self.status_label.pack(side='left', padx=10, pady=5)
        
        # Initialize variables
        self.input_file = None
        self.selected_sheet = None
        self.scraper = None
        self.is_running = False
        self.current_row = 0
        self.total_rows = 0
        
        self.setup_logging()

    def setup_styles(self):
        """Configure ttk styles for better appearance"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure accent button style
        style.configure('Accent.TButton', 
                       background='#3498db', 
                       foreground='white',
                       font=('Arial', 10, 'bold'))
        
        # Configure progress bar style
        style.configure("Horizontal.TProgressbar", 
                       troughcolor='#ecf0f1', 
                       background='#27ae60',
                       lightcolor='#2ecc71',
                       darkcolor='#27ae60')

    def setup_logging(self):
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget

            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.configure(state=NORMAL)
                    self.text_widget.insert(END, msg + '\n')
                    self.text_widget.configure(state=DISABLED)
                    self.text_widget.see(END)
                self.text_widget.after(0, append)

        handler = TextHandler(self.log_text)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', 
                                    datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(handler)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_path:
            self.input_file = file_path
            self.file_label.config(text=os.path.basename(file_path), fg="green")
            self.load_sheets(file_path)
    
    def load_sheets(self, file_path):
        try:
            excel_file = pd.ExcelFile(file_path)
            sheets = excel_file.sheet_names
            self.sheet_combo['values'] = sheets
            if sheets:
                self.sheet_combo.set(sheets[0])  # Set first sheet as default
                self.selected_sheet = sheets[0]
                logging.info(f"✅ Loaded {len(sheets)} sheets: {', '.join(sheets)}")
                logging.info(f"📋 Default sheet: {sheets[0]}")
                self.status_var.set(f"Loaded {len(sheets)} sheets")
            else:
                logging.error("❌ No sheets found in the Excel file")
                self.status_var.set("No sheets found")
        except Exception as e:
            logging.error(f"❌ Error loading sheets: {str(e)}")
            self.status_var.set("Error loading sheets")
    
    def on_sheet_selected(self, event=None):
        self.selected_sheet = self.sheet_var.get()
        logging.info(f"📋 Selected sheet: {self.selected_sheet}")
        self.start_button.config(state=NORMAL)
        self.status_var.set(f"Sheet selected: {self.selected_sheet}")
    
    def clear_log(self):
        """Clear the log text widget"""
        self.log_text.configure(state=NORMAL)
        self.log_text.delete('1.0', END)
        self.log_text.configure(state=DISABLED)
        logging.info("🧹 Log cleared")
    
    def stop_scraping(self):
        """Stop the scraping process"""
        self.is_running = False
        self.stop_button.config(state=DISABLED)
        self.start_button.config(state=NORMAL)
        self.select_button.config(state=NORMAL)
        self.progress_var.set("Scraping stopped by user")
        self.status_var.set("Stopped")
        logging.info("⏹️ Scraping stopped by user")

    def start_scraping(self):
        self.is_running = True
        self.start_button.config(state=DISABLED)
        self.stop_button.config(state=NORMAL)
        self.select_button.config(state=DISABLED)
        self.log_text.configure(state=NORMAL)
        self.log_text.delete('1.0', END)
        self.log_text.configure(state=DISABLED)
        
        # Initialize scraper with user settings
        headless = bool(self.headless_var.get())
        self.scraper = DueAmountScraper(headless=headless)
        
        self.status_var.set("Starting scraping...")
        logging.info("🚀 Starting scraping process...")
        threading.Thread(target=self.run_scraping, daemon=True).start()

    def update_progress(self, current, total):
        """Update progress bar and label"""
        percentage = (current / total) * 100
        self.progress_bar['value'] = percentage
        self.progress_var.set(f"Processing {current}/{total} ({percentage:.1f}%)")
        self.status_var.set(f"Processing URL {current} of {total}")
        self.root.update_idletasks()
    
    def check_stop(self):
        """Check if scraping should be stopped"""
        return not self.is_running
    
    def run_scraping(self):
        try:
            delay = float(self.delay_var.get())
            max_workers = int(self.thread_var.get())
            results = self.scraper.process_links(
                input_file=self.input_file, 
                sheet_name=self.selected_sheet,
                delay=delay,
                progress_callback=self.update_progress,
                stop_callback=self.check_stop,
                max_workers=max_workers
            )

            if results is not None and self.is_running:
                total = len(results)
                success = len(results[results['Status'] == 'Success'])
                failed = total - success

                msg = (f"✅ Scraping completed!\n\n"
                       f"📊 Total URLs processed: {total}\n"
                       f"✅ Successful extractions: {success}\n"
                       f"❌ Failed extractions: {failed}\n"
                       f"📈 Success rate: {(success/total*100):.1f}%\n\n"
                       f"💾 Results saved to {self.input_file}")

                logging.info("🎉 " + msg.replace('\n', ' '))
                self.progress_var.set(f"Completed! {success}/{total} successful")
                self.status_var.set("Completed successfully")
                messagebox.showinfo("Scraping Complete", msg)
            elif not self.is_running:
                logging.info("⏹️ Scraping was stopped by user")
                self.progress_var.set("Stopped by user")
                self.status_var.set("Stopped")
            else:
                messagebox.showerror("Error", "Failed to process the file or extract data.")
                self.status_var.set("Error occurred")
        except Exception as e:
            logging.error(f"❌ Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            self.status_var.set("Error occurred")
        finally:
            self.is_running = False
            self.start_button.config(state=NORMAL)
            self.stop_button.config(state=DISABLED)
            self.select_button.config(state=NORMAL)

def main():
    root = Tk()
    app = ScraperApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
