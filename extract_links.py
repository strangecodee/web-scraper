import pandas as pd
import tkinter as tk
from tkinter import filedialog

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    print("Please select the Excel file to upload...")
    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx;*.xls")]
    )

    if not file_path:
        print("No file selected.")
        return

    try:
        df = pd.read_excel(file_path)
        if 'link' in df.columns:
            links = df['link'].tolist()
            with open('links.txt', 'w') as f:
                for link in links:
                    f.write(f"{link}\n")
            print(f"Links extracted successfully from {file_path} and saved to links.txt")
        else:
            print("Error: 'link' column not found in the Excel file.")
    except FileNotFoundError:
        print("Error: The specified Excel file was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
