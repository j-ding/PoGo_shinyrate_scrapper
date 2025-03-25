# Pokemon Shiny Rates Scraper

A simple web scraper that collects Pokemon shiny encounter rates from [shinyrates.com](https://shinyrates.com/) and saves them to CSV files for analysis.

## Overview

This tool automatically scrapes the latest shiny rates for Pokemon, calculates percentages, and exports the data in a sorted format (highest shiny rates first). It generates two CSV files:
- A timestamped version (e.g., `shiny_rates_20240324_123456.csv`)
- A "latest" version (`shiny_rates_latest.csv`) that gets overwritten with each run

The data includes Pokemon ID, name, shiny rate (as a fraction), shiny rate percentage, and sample size.

## Requirements

- Python 3.7+
- Playwright for Python
- Chrome/Chromium browser (installed automatically by Playwright)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/pokemon-shiny-scraper.git
   cd pokemon-shiny-scraper
   ```

2. Install the required packages:
   ```bash
   pip install playwright
   ```

3. Install the browser drivers:
   ```bash
   python -m playwright install chromium
   ```

## Usage

Run the script with Python:

```bash
python shiny_scraper.py
```

The script will:
1. Create a `data` directory if it doesn't exist
2. Launch a headless browser
3. Navigate to shinyrates.com
4. Extract Pokemon data
5. Calculate and sort shiny rates
6. Save the results to CSV files in the `data` directory

## Output Format

The CSV files contain the following columns:

- **ID**: Pokemon ID number
- **Name**: Pokemon name
- **Shiny Rate**: The fraction representing encounters per shiny (e.g., '1/500')
- **Shiny Rate Percent**: The percentage chance of encountering a shiny (e.g., '0.2000%')
- **Sample Size**: Number of encounters recorded to calculate the rate

## Notes

- The script handles fractions in the CSV output by adding a single quote prefix to prevent Excel from interpreting them as dates.
- The script sorts Pokemon by highest shiny rate (most common) to lowest.
- A new timestamped file is created each time for historical tracking.

## License

[MIT License](LICENSE)

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/yourusername/pokemon-shiny-scraper/issues).

## Disclaimer

This tool is for educational purposes only. Please be respectful of the shinyrates.com website by not running this scraper excessively.
