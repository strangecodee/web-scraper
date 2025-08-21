# 🕸️ Web Scraper – Automated Due Amount Extractor  

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python)  
![Selenium](https://img.shields.io/badge/Selenium-Automation-green.svg?logo=selenium)  
![Status](https://img.shields.io/badge/Status-Active-success.svg)  

---

## 📌 Overview  

This project is a **web scraping automation tool** built with **Python + Selenium**.  
It extracts **due amounts** from a given list of URLs and stores the results into an **Excel file** using **Pandas**.  

🔹 Perfect for automating repetitive financial checks.  
🔹 Reads input URLs from Google Sheets or Excel.  
🔹 Writes scraped data back to an output sheet.  

---

## 📂 Project Structure
- `enhanced_scrape_dues.py` → Main script  
- `requirements.txt` → Python dependencies  
- `README.md` → Project documentation  
- `output.xlsx` → (Generated) Output file with scraped data  





---

## ⚡ Setup Instructions  

### 1️⃣ Clone the repository  
```bash
git clone https://github.com/strangecodee/web-scraper.git
cd web-scraper
```
### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```
 ### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
### ▶️ Running the Script
```bash
python enhanced_scrape_dues.py
```

### The script will open Chrome using Selenium

- Visit all URLs (from your list / Google Sheet)

- Extract due amounts

- Save results to output.xlsx

## 📊 Example Output (Excel)

After running the script, an `output.xlsx` file will be generated.  
It contains the scraped results in the following format:

## 📊 Example Output (Excel)

After running the scraper, an `output.xlsx` file will be generated with the following structure:

| Portfolio's | Agent            | Mtd | Loan ID      | Link                                                                                                                                     | Due Amount |
|-------------|------------------|-----|--------------|------------------------------------------------------------------------------------------------------------------------------------------|------------|
| MONEY VIEW  | Surabhi (MV NPA) |     | 1.03461E+11  | [Open](https://moneyview.whizdm.com/payment/init?l=ff808081925184b40192550850906f73&paymentIntent=dues&source=web&originSource=agency)  | 8059       |
| MONEY VIEW  | Surabhi (MV NPA) |     | 1.49486E+11  | [Open](https://moneyview.whizdm.com/payment/init?l=ff808081901f526f019021881aeb5bce&paymentIntent=dues&source=web&originSource=agency)  | 19420      |
| MONEY VIEW  | Surabhi (MV NPA) |     | 1.03091E+11  | [Open](https://moneyview.whizdm.com/payment/init?l=ff8080818fed91e7018fef1521e249e4&paymentIntent=dues&source=web&originSource=agency)  | 35516      |
| MONEY VIEW  | Surabhi (MV NPA) |     | 1.39459E+11  | [Open](https://moneyview.whizdm.com/payment/init?l=ff8080819208c605019209b12d49609c&paymentIntent=dues&source=web&originSource=agency)  | 8112       |


### 🛠️ Tech Stack

### 🐍 Python 3.8+

### 🌐 Selenium (Web automation)

### 📊 Pandas (Data handling)

### 📑 OpenPyXL (Excel support)

### 🧑‍💻 Author

*👤 Anurag Maurya* 
[<img src="https://img.icons8.com/color/48/000000/linkedin.png" width="30"/>](https://www.linkedin.com/in/annuragmaurya/)

💻 Cloud & DevOps Enthusiast | Python Developer

### ⭐ Contributing

Contributions are welcome!
If you'd like to improve this scraper, feel free to fork the repo and submit a pull request.

### 📜 License

This project is licensed under the MIT License – feel free to use and modify it.



This project is licensed under the MIT License.

<p align="center">Made with ❤️ by <a href="https://github.com/strangecodee">Anurag Maurya</a></p> ```
