# api_server.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os
import datetime
from playwright.sync_api import sync_playwright
import csv

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Global variables to store data
pokemon_data = []
last_updated = None
DATA_FILE = 'data/latest_data.json'
os.makedirs('data', exist_ok=True)

def scrape_shiny_rates():
    """Run the scraper and return the results"""
    results = []
    
    try:
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
                    results.append({
                        "id": pokemon_id,
                        "name": pokemon_name,
                        "rate": shiny_rate,
                        "percent": rate_percent,
                        "sample_size": sample_size,
                        "rate_value": rate_value
                    })
                except Exception as e:
                    print(f"Error processing row: {str(e)}")
            
            browser.close()
            
            # Sort data by shiny rate value (largest first)
            print(f"Sorting {len(results)} Pokemon by shiny rate...")
            results = sorted(results, key=lambda x: x["rate_value"], reverse=True)
            
            return results
    except Exception as e:
        print(f"Scraping error: {str(e)}")
        return []

def update_data():
    """Function to update the data and save it"""
    global pokemon_data, last_updated
    
    try:
        print("Running scheduled data update...")
        new_data = scrape_shiny_rates()
        
        if new_data and len(new_data) > 0:
            pokemon_data = new_data
            last_updated = datetime.datetime.now().isoformat()
            
            # Save to file
            with open(DATA_FILE, 'w') as f:
                json.dump({
                    "data": pokemon_data,
                    "last_updated": last_updated
                }, f)
            
            print(f"Data updated successfully with {len(pokemon_data)} Pokemon")
        else:
            print("Scrape returned no data, keeping existing data")
    except Exception as e:
        print(f"Error updating data: {str(e)}")

# Load existing data if available
def load_existing_data():
    global pokemon_data, last_updated
    
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                saved_data = json.load(f)
                pokemon_data = saved_data.get("data", [])
                last_updated = saved_data.get("last_updated", None)
                print(f"Loaded {len(pokemon_data)} Pokemon from saved data")
    except Exception as e:
        print(f"Error loading saved data: {str(e)}")

# Set up scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_data, trigger="interval", hours=6)
scheduler.start()

# API endpoints
@app.route('/api/shiny-rates', methods=['GET'])
def get_shiny_rates():
    """Return all shiny rates data"""
    return jsonify({
        "data": pokemon_data,
        "last_updated": last_updated
    })

@app.route('/api/pokemon/<pokemon_id>', methods=['GET'])
def get_pokemon(pokemon_id):
    """Return data for a specific Pokemon by ID"""
    for pokemon in pokemon_data:
        if pokemon["id"] == pokemon_id:
            return jsonify(pokemon)
    return jsonify({"error": "Pokemon not found"}), 404

@app.route('/api/refresh', methods=['GET'])
def refresh_data():
    """Manually trigger a data refresh"""
    update_data()
    return jsonify({
        "status": "success",
        "message": "Data refresh initiated",
        "last_updated": last_updated
    })

@app.route('/api/search', methods=['GET'])
def search_pokemon():
    """Search for Pokemon by name"""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({"error": "No search query provided"}), 400
    
    results = [p for p in pokemon_data if query in p["name"].lower()]
    return jsonify({
        "results": results,
        "count": len(results)
    })

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Return categorized Pokemon data"""
    if not pokemon_data:
        return jsonify({"error": "No data available"}), 404
    
    # Get top 20 and bottom 20
    top_20 = pokemon_data[:20]
    bottom_20 = pokemon_data[-20:] if len(pokemon_data) >= 20 else []
    
    # Find some common Pokemon (this is just an example, you might want to customize)
    common_ids = ["1", "4", "7", "25", "133"]  # Bulbasaur, Charmander, Squirtle, Pikachu, Eevee
    common_pokemon = [p for p in pokemon_data if p["id"] in common_ids]
    
    return jsonify({
        "top_rates": top_20,
        "lowest_rates": bottom_20,
        "common_pokemon": common_pokemon,
        "last_updated": last_updated
    })

if __name__ == '__main__':
    # Load existing data on startup
    load_existing_data()
    
    # If no data, run initial scrape
    if not pokemon_data:
        print("No existing data found, running initial scrape...")
        update_data()
    
    # Start the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
