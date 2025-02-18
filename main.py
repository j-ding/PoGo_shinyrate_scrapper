from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import csv
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"  # Update this path if necessary
chrome_options.add_argument("--headless")  # Optional: run in headless mode

# Set up the WebDriver
service = Service(r'C:\Users\Ding\Documents\chromedriver-win64\chromedriver.exe')

# Create a new instance of the Chrome driver
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL of the website to scrape
URL = "https://shinyrates.com/"
driver.get(URL)

# Wait for the page to load
time.sleep(5)  # Adjust the sleep time as necessary

# Find the table body
tbody = driver.find_element(By.ID, 'table_body')

# Extract rows from the table body
rows = tbody.find_elements(By.TAG_NAME, 'tr')
print(f"Number of rows found: {len(rows)}")

data = []

# Extract data from each row
for row in rows:
    cols = row.find_elements(By.TAG_NAME, 'td')
    print(f"Columns found in row: {len(cols)}")  # Debugging: print number of columns in each row
    if len(cols) < 4:  # Adjusted to check for 4 columns
        print("Skipping row due to insufficient columns.")  # Debugging
        continue
    
    # Extracting data
    ids  = cols[0].text.strip() 
    name = cols[1].text.strip()  # Adjusted index based on actual column structure
    shiny_rate = cols[2].text.strip().replace(',', '')  # Remove commas
    sample_size = cols[3].text.strip().replace(',', '')  # Remove commas
    
    if '/' in shiny_rate:
        shiny_rate = "'" + shiny_rate
    if '/' in sample_size:
        sample_size = "'" + sample_size
    
    print(f"Extracted Data - ID: {ids}, Name: {name}, Shiny Rate: {shiny_rate}, Sample Size: {sample_size}")  # Debugging
    data.append([ids, name, shiny_rate, sample_size])

# Save data to CSV
csv_filename = "shiny_rates.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["ID","Name", "Shiny Rate", "Sample Size"])
    writer.writerows(data)

print(f"Data saved to {csv_filename}")

# Close the driver
driver.quit()
