# Simple version with minimal dependencies
from playwright.sync_api import sync_playwright
import csv
import re
import os
import datetime

def run_simple_scraper():
    # Create data directory if it doesn't exist
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Starting shiny rate scraper...")
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Go to the website
        print("Loading shinyrates.com...")
        page.goto("https://shinyrates.com/", timeout=30000)
        page.wait_for_load_state("networkidle")
        
        # Get all table rows (skip header)
        print("Finding Pokemon data...")
        rows = page.query_selector_all("tr")
        
        data = []
        for row in rows[1:]:  # Skip header row
            try:
                # Get all cells in this row
                cells = row.query_selector_all("td")
                
                # Check if we have enough cells
                if len(cells) < 4:
                    continue
                
                # Extract data from cells
                pokemon_id = cells[0].inner_text().strip()
                pokemon_name = cells[1].inner_text().strip()
                shiny_rate = cells[2].inner_text().strip()
                sample_size = cells[3].inner_text().strip() if len(cells) > 3 else ""
                
                # Calculate percentage for sorting
                rate_value = 0.0
                if "/" in shiny_rate:
                    parts = shiny_rate.split("/")
                    if len(parts) == 2 and parts[1].isdigit():
                        rate_value = float(parts[0]) / float(parts[1])
                
                # Format rate percentage
                rate_percent = f"{rate_value * 100:.4f}%"
                
                # Add quotes to fractions for CSV
                if "/" in shiny_rate:
                    shiny_rate = "'" + shiny_rate
                
                print(f"Found: {pokemon_name} - {shiny_rate}")
                data.append([pokemon_id, pokemon_name, shiny_rate, rate_percent, sample_size, rate_value])
            except Exception as e:
                print(f"Error processing row: {str(e)}")
        
        browser.close()
        
        # Sort data by shiny rate value (largest first)
        print(f"Sorting {len(data)} Pokemon by shiny rate...")
        sorted_data = sorted(data, key=lambda x: x[5], reverse=True)
        
        # Remove sorting column
        sorted_data = [row[:5] for row in sorted_data]
        
        # Save to CSV files
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = os.path.join(output_dir, f"shiny_rates_{timestamp}.csv")
        latest_filename = os.path.join(output_dir, "shiny_rates_latest.csv")
        
        # Write timestamped file
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Shiny Rate", "Shiny Rate Percent", "Sample Size"])
            writer.writerows(sorted_data)
        
        # Write latest file
        with open(latest_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Shiny Rate", "Shiny Rate Percent", "Sample Size"])
            writer.writerows(sorted_data)
        
        print(f"Data saved to {csv_filename} and {latest_filename}")

if __name__ == "__main__":
    run_simple_scraper()
