"""
Utility functions for Airbnb Scraper
"""

import time
import random
import os
import re
import pandas as pd
from typing import List, Dict
import requests
from config import REQUEST_DELAY, PROXY_LIST, USE_PROXIES

def create_output_folder():
    """Create output folder if it doesn't exist"""
    if not os.path.exists("output"):
        os.makedirs("output")

def get_random_proxy():
    """Get a random proxy from the proxy list"""
    if USE_PROXIES and PROXY_LIST:
        return random.choice(PROXY_LIST)
    return None

def add_delay():
    """Add random delay between requests"""
    delay = REQUEST_DELAY + random.uniform(0, 2)
    time.sleep(delay)

def clean_price(price_text: str) -> str:
    """Clean and format price text with original currency symbol"""
    if not price_text:
        return "N/A"
    
    # Match symbol and numeric value
    match = re.search(r"(?P<symbol>[£$€])\s?(?P<amount>[\d,]+(?:\.\d{1,2})?)", price_text)
    if match:
        symbol = match.group("symbol")
        amount = match.group("amount").replace(",", "")
        try:
            float(amount)  # Validate numeric
            return f"{symbol}{amount}"
        except ValueError:
            return "N/A"
    
    return "N/A"

def clean_text(text: str) -> str:
    """Clean and format text content"""
    if not text:
        return "N/A"
    
    return text.strip().replace("\n", " ").replace("\r", "")

def save_to_csv(data: List[Dict], filename: str):
    """Save scraped data to CSV file"""
    create_output_folder()
    filepath = os.path.join("output", filename)
    
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"Data saved to {filepath}")

def save_to_excel(data: List[Dict], filename: str):
    """Save scraped data to Excel file"""
    create_output_folder()
    filepath = os.path.join("output", filename)
    
    df = pd.DataFrame(data)
    df.to_excel(filepath, index=False, engine='openpyxl')
    print(f"Data saved to {filepath}")

def validate_url(url: str) -> bool:
    """Validate if URL is accessible"""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except:
        return False

def format_city_for_url(city: str) -> str:
    """Format city name for Airbnb URL"""
    return city.replace(" ", "-").replace(",", "--")

def generate_airbnb_search_url(city: str) -> str:
    """Generate Airbnb search URL for a given city"""
    formatted_city = format_city_for_url(city)
    base_url = "https://www.airbnb.com/s"
    return f"{base_url}/{formatted_city}/homes"
