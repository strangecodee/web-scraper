import pandas as pd

try:
    # Read the Excel file
    df = pd.read_excel('New Microsoft Office Excel Worksheet (3) (1).xlsx')

    # Check if the 'link' column exists
    if 'link' in df.columns:
        # Get the links from the 'link' column
        links = df['link'].tolist()

        # Save the links to a text file
        with open('links.txt', 'w') as f:
            for link in links:
                f.write(f"{link}\n")
        print("Links extracted successfully and saved to links.txt")
    else:
        print("Error: 'link' column not found in the Excel file.")

except FileNotFoundError:
    print("Error: The specified Excel file was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
