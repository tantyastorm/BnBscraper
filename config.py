"""
Configuration file for Airbnb Scraper
"""

# Target cities for scraping
CITIES = [
    "New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX",
    "Phoenix, AZ", "Philadelphia, PA", "San Antonio, TX", "San Diego, CA",
    "Dallas, TX", "San Jose, CA", "Austin, TX", "Jacksonville, FL",
    "Fort Worth, TX", "Columbus, OH", "Charlotte, NC", "San Francisco, CA",
    "Indianapolis, IN", "Seattle, WA", "Denver, CO", "Washington, DC",
    "Boston, MA", "El Paso, TX", "Nashville, TN", "Detroit, MI",
    "Oklahoma City, OK", "Portland, OR", "Las Vegas, NV", "Memphis, TN",
    "Louisville, KY", "Baltimore, MD", "Milwaukee, WI", "Albuquerque, NM",
    "Tucson, AZ", "Fresno, CA", "Mesa, AZ", "Sacramento, CA",
    "Atlanta, GA", "Kansas City, MO", "Colorado Springs, CO", "Miami, FL",
    "Raleigh, NC", "Omaha, NE", "Long Beach, CA", "Virginia Beach, VA",
    "Oakland, CA", "Minneapolis, MN", "Tulsa, OK", "Arlington, TX",
    "Tampa, FL", "New Orleans, LA"
]

# Scraping settings
LISTINGS_PER_CITY = 10
REQUEST_DELAY = 2  # seconds between requests
TIMEOUT = 30  # request timeout in seconds

# Headers for requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Proxy settings (optional)
USE_PROXIES = False
PROXY_LIST = [
    # Add your proxy list here if needed
    # "http://proxy1:port",
    # "http://proxy2:port",
]

# Output settings
OUTPUT_FOLDER = "output"
CSV_FILENAME = "airbnb_listings.csv"
EXCEL_FILENAME = "airbnb_listings.xlsx"
