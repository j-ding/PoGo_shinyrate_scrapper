from playwright.sync_api import sync_playwright
import csv
import re
import os
import datetime

def run_improved_scraper():
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
                
                # Clean up shiny rate format (remove any apostrophes)
                shiny_rate = shiny_rate.replace("'", "")
                
                # Calculate percentage for sorting
                rate_value = 0.0
                if "/" in shiny_rate:
                    parts = shiny_rate.split("/")
                    if len(parts) == 2 and parts[1].replace(",", "").isdigit():
                        numerator = float(parts[0])
                        denominator = float(parts[1].replace(",", ""))
                        if denominator > 0:  # Avoid division by zero
                            rate_value = numerator / denominator
                
                # Format rate percentage with 4 decimal places
                rate_percent = f"{rate_value * 100:.4f}%"
                
                # Format sample size with commas for thousands
                if sample_size and sample_size.replace(",", "").isdigit():
                    sample_size = "{:,}".format(int(sample_size.replace(",", "")))
                
                print(f"Found: {pokemon_name} - {shiny_rate} ({rate_percent})")
                data.append([pokemon_id, pokemon_name, shiny_rate, rate_percent, sample_size, rate_value])
            except Exception as e:
                print(f"Error processing row: {str(e)}")
        
        browser.close()
        
        # Sort data by shiny rate value (largest first)
        print(f"Sorting {len(data)} Pokemon by shiny rate...")
        sorted_data = sorted(data, key=lambda x: x[5], reverse=True)
        
        # Remove sorting column
        sorted_data = [row[:5] for row in sorted_data]
        
        # Create categorized data for readable output
        highest_rates = sorted_data[:20]  # Top 20 highest rates
        lowest_rates = sorted_data[-20:]  # 20 lowest rates
        
        # Save to CSV files
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = os.path.join(output_dir, f"shiny_rates_{timestamp}.csv")
        latest_filename = os.path.join(output_dir, "shiny_rates_latest.csv")
        readable_filename = os.path.join(output_dir, "shiny_rates_readable.txt")
        
        # Write timestamped CSV file
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Shiny Rate", "Shiny Rate Percent", "Sample Size"])
            writer.writerows(sorted_data)
        
        # Write latest CSV file
        with open(latest_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Shiny Rate", "Shiny Rate Percent", "Sample Size"])
            writer.writerows(sorted_data)
        
        # Write human-readable text file with categories
        with open(readable_filename, "w", encoding="utf-8") as f:
            f.write("Pokemon Shiny Rates Report\n")
            f.write("=========================\n")
            f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("TOP 20 HIGHEST SHINY RATES\n")
            f.write("=========================\n")
            f.write(f"{'ID':<6} {'Pokemon':<15} {'Shiny Rate':<12} {'Percentage':<12} {'Sample Size':<12}\n")
            f.write("-" * 60 + "\n")
            for row in highest_rates:
                f.write(f"{row[0]:<6} {row[1]:<15} {row[2]:<12} {row[3]:<12} {row[4]:<12}\n")
            
            f.write("\n\n20 LOWEST SHINY RATES\n")
            f.write("=========================\n")
            f.write(f"{'ID':<6} {'Pokemon':<15} {'Shiny Rate':<12} {'Percentage':<12} {'Sample Size':<12}\n")
            f.write("-" * 60 + "\n")
            for row in lowest_rates:
                f.write(f"{row[0]:<6} {row[1]:<15} {row[2]:<12} {row[3]:<12} {row[4]:<12}\n")
            
            f.write("\n\nALL POKEMON SHINY RATES\n")
            f.write("=========================\n")
            f.write(f"{'ID':<6} {'Pokemon':<15} {'Shiny Rate':<12} {'Percentage':<12} {'Sample Size':<12}\n")
            f.write("-" * 60 + "\n")
            for row in sorted_data:
                f.write(f"{row[0]:<6} {row[1]:<15} {row[2]:<12} {row[3]:<12} {row[4]:<12}\n")
        
        print(f"Data saved to {csv_filename} and {latest_filename}")
        print(f"Human-readable report saved to {readable_filename}")

if __name__ == "__main__":
    run_improved_scraper()
