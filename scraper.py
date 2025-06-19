"""
Core scraping functionality for Airbnb listings
"""

import re
import logging
from typing import List, Dict, Optional, Union
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import requests
from bs4 import BeautifulSoup

from config import HEADERS, TIMEOUT, LISTINGS_PER_CITY
from utils import add_delay, get_random_proxy, clean_price, clean_text, generate_airbnb_search_url

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AirbnbScraper:
    def __init__(self, use_selenium: bool = True):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.use_selenium = use_selenium
        self.driver = None

        if self.use_selenium:
            self.setup_selenium()

    def setup_selenium(self):
        """Setup Selenium WebDriver with stealth mode"""
        try:
            chrome_options = Options()
            # Uncomment for headless mode if needed
            # chrome_options.add_argument("--headless")
            # chrome_options.add_argument("--headless=new") 
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-features=VoiceTranscription")
            chrome_options.add_argument("--disable-speech-api")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)

            user_agent = HEADERS.get(
                "User-Agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36",
            )
            chrome_options.add_argument(f"user-agent={user_agent}")

            self.driver = webdriver.Chrome(options=chrome_options)

            stealth(
                self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )

            self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent})

            logger.info("Selenium WebDriver initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            self.use_selenium = False

    def scrape_city_listings(self, city: str, callback=None) -> List[Dict]:
        logger.info(f"Scraping listings for {city}")

        listings = []
        url = generate_airbnb_search_url(city)

        try:
            if self.use_selenium and self.driver:
                listings = self._scrape_with_selenium(url, city, callback)
            else:
                listings = self._scrape_with_requests(url, city, callback)
        except Exception as e:
            logger.error(f"Error scraping {city}: {e}")
            if callback:
                callback(f"Error scraping {city}: {e}")

        logger.info(f"Found {len(listings)} listings for {city}")
        return listings

    def _accept_cookies(self):
        if not self.driver:
            logger.warning("Selenium driver not initialized; cannot accept cookies.")
            return
        try:
            # Wait longer in case popup is slow
            wait = WebDriverWait(self.driver, 15)

            # Try different possible button texts, sometimes sites use slight variations
            possible_texts = ['Accept all', 'Accept cookies', 'Agree', 'I agree', 'Accept']

            accept_button = None
            for text in possible_texts:
                try:
                    accept_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, f'//button[contains(text(), "{text}")]'))
                    )
                    if accept_button:
                        break
                except:
                    continue

            if accept_button:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", accept_button)
                accept_button.click()
                logger.info("Accepted cookies successfully.")
            else:
                logger.info("No cookie acceptance button found or already accepted.")
        except Exception as e:
            logger.warning(f"Failed to accept cookies: {e}")


    def _scrape_with_selenium(self, url: str, city: str, callback=None) -> List[Dict]:
        listings = []
        if not self.driver:
            logger.error("Selenium driver is not initialized; cannot scrape.")
            return listings
        try:
            self.driver.get(url)
            self._accept_cookies()

            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='listing-card-title']"))
            )

            listing_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='card-container']")

            for i, element in enumerate(listing_elements[:LISTINGS_PER_CITY]):
                try:
                    data = self._extract_listing_data_selenium(element, city)
                    if data:
                        listings.append(data)

                    if callback:
                        callback(f"Scraped {i+1}/{min(len(listing_elements), LISTINGS_PER_CITY)} listings from {city}")
                except Exception as e:
                    logger.error(f"Error extracting listing data: {e}")
                    continue
        except Exception as e:
            logger.error(f"Selenium scraping error: {e}")

        return listings

    def _scrape_with_requests(self, url: str, city: str, callback=None) -> List[Dict]:
        listings = []
        try:
            proxy = get_random_proxy()
            proxies = {"http": proxy, "https": proxy} if proxy else None

            response = self.session.get(url, proxies=proxies, timeout=TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "lxml")
            listing_elements = soup.find_all("div", class_="lxq01kf")[:LISTINGS_PER_CITY]

            for i, element in enumerate(listing_elements):
                try:
                    data = self._extract_listing_data_bs4(element, city)
                    if data:
                        listings.append(data)
                    if callback:
                        callback(f"Scraped {i+1}/{len(listing_elements)} listings from {city}")
                except Exception as e:
                    logger.error(f"Error extracting listing data: {e}")
                    continue
                add_delay()

        except Exception as e:
            logger.error(f"Requests scraping error: {e}")

        return listings

    def _extract_listing_data_selenium(self, element, city: str) -> Optional[Dict]:
        if not self.driver:
            logger.warning("Selenium driver is not initialized; cannot extract listing data.")
            return None

        try:
            # Name
            try:
                name_el = WebDriverWait(element, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='listing-card-title']"))
                )
                name = clean_text(name_el.text)
            except Exception:
                return None

            # Subtitle
            try:
                subtitle_el = element.find_element(By.CSS_SELECTOR, "[data-testid='listing-card-name']")
                subtitle = clean_text(subtitle_el.text)
                if subtitle:
                    name = f"{name} — {subtitle}"
            except Exception:
                pass

            # Prices
            price = original_price = "N/A"
            try:
                price_txt = element.find_element(By.CSS_SELECTOR, "._w3xh25").text
                found = re.findall(r"£\d[\d,]*", price_txt)
                if found:
                    if len(found) == 1:
                        price = clean_price(found[0])
                    else:
                        original_price = clean_price(found[0])
                        price = clean_price(found[1])
            except Exception:
                pass

            if price == "N/A" and original_price == "N/A":
                return None

            # URL
            url = "N/A"
            try:
                href = element.find_element(By.TAG_NAME, "a").get_attribute("href")
                if href:
                    url = href if href.startswith("http") else f"https://www.airbnb.com{href}"
            except Exception:
                pass

            # Location
            location = city
            try:
                loc_txt = element.find_element(By.CSS_SELECTOR, "[class*='atm_7l_1kw7nm4']").text
                location = clean_text(loc_txt.splitlines()[0])
            except Exception:
                pass

            # Rating and reviews (optional)
            # Skipped here, but can be added if needed

            return {
                "name": name,
                "price": price,
                "original_price": original_price,
                "location": location,
                "url": url,
                "city": city,
            }

        except Exception as e:
            logger.error(f"Error extracting listing: {e}")
            return None

    def _extract_listing_data_bs4(self, element, city: str) -> Optional[Dict]:
        try:
            name_elem = element.find("div", class_="t1jojoys")
            name = clean_text(name_elem.get_text()) if name_elem else "N/A"

            price_elem = element.find("span", class_="_1p7iugi")
            price = clean_price(price_elem.get_text()) if price_elem else "N/A"

            location_elem = element.find("div", class_="fb4nyux")
            location = clean_text(location_elem.get_text()) if location_elem else city

            url = "N/A"
            url_elem = element.find("a")
            if url_elem:
                href = url_elem.get("href")
                if href:
                    url = href if href.startswith("http") else f"https://www.airbnb.com{href}"

            return {
                "name": name,
                "price": price,
                "location": location,
                "url": url,
                "city": city,
            }
        except Exception as e:
            logger.error(f"Error extracting BS4 data: {e}")
            return None

    def scrape_multiple_cities(self, cities: List[str], callback=None) -> List[Dict]:
        all_listings = []
        for i, city in enumerate(cities):
            if callback:
                callback(f"Processing city {i+1}/{len(cities)}: {city}")

            city_listings = self.scrape_city_listings(city, callback)
            all_listings.extend(city_listings)

            if i < len(cities) - 1:
                add_delay()
        return all_listings

    def close(self):
        if self.driver:
            self.driver.quit()
        self.session.close()
