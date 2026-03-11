import abc
import time
import random
import requests
import pandas as pd
from loguru import logger
from fake_useragent import UserAgent
from pathlib import Path
from datetime import datetime
from src.config.settings import LOGS_DIR, RAW_DATA_DIR, MAX_RETRIES, DELAY_BETWEEN_REQUESTS

# Set up logging to the logs folder with a date-based filename
logger.add(f"{LOGS_DIR}/scrape_{datetime.now().strftime('%Y-%m-%d')}.log", rotation="10 MB")

class BaseScraper(abc.ABC):
    def __init__(self, store_name):
        self.store_name = store_name
        self.ua = UserAgent()
        self.session = requests.Session()
        self.seen_urls = set()  # Unique guard for products (resettable)

    def reset_unique_guard(self):
        """Clears memory of seen products to allow re-extracting for a new city."""
        self.seen_urls = set()
        logger.info(f"[{self.store_name}] Unique guard reset for new city/branch.")

    def get_headers(self):
        """Generates random browser headers for every request."""
        return {
            "User-Agent": self.ua.random,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }

    def fetch_static(self, url):
        """
        Fetches static HTML content using requests with:
        - Retry logic (Exponential backoff)
        - Session reuse
        - Random user agents
        """
        retries = 0
        while retries < MAX_RETRIES:
            try:
                # Rate limiting: Sleep before request
                time.sleep(random.uniform(*DELAY_BETWEEN_REQUESTS))
                
                logger.info(f"[{self.store_name}] Fetching: {url}")
                response = self.session.get(url, headers=self.get_headers(), timeout=30)
                response.raise_for_status()
                
                return response.text
                
            except Exception as e:
                retries += 1
                wait_time = 2 ** retries
                logger.warning(f"[{self.store_name}] Error fetching {url}: {e}. Retrying in {wait_time}s... ({retries}/{MAX_RETRIES})")
                time.sleep(wait_time)
                
        logger.error(f"[{self.store_name}] Failed to fetch {url} after {MAX_RETRIES} attempts.")
        return None

    def save_page_to_csv(self, data_list, city, category):
        """
        Saves a list of dictionaries to a raw CSV immediately.
        Append mode allows us to save page-by-page.
        Includes a 'Unique Guard' to prevent saving duplicates in the same run.
        """
        if not data_list:
            logger.warning(f"[{self.store_name}] No data collected to save.")
            return

        # Filter against seen_urls
        unique_data = []
        for item in data_list:
            url = item.get("product_url")
            # If URL is N/A (like Chase Up often is), we use name + price as a fallback key
            if not url or url == "N/A":
                url = f"{item['product_name']}-{item['price']}"
            
            if url not in self.seen_urls:
                self.seen_urls.add(url)
                unique_data.append(item)
        
        if not unique_data:
            return

        data_list = unique_data

        # Ensure consistent column structure
        columns = [
            'store_name', 'city', 'category', 'product_name', 'brand', 
            'price', 'quantity', 'unit', 'image_url', 'product_url', 'scraped_at'
        ]
        
        # Determine filename
        today = datetime.now().strftime('%Y-%m-%d')
        filename = f"{self.store_name}_{city}_{category}_{today}.csv"
        file_path = RAW_DATA_DIR / filename

        try:
            df = pd.DataFrame(data_list)
            # Reorder columns to ensure consistency across scrapers
            for col in columns:
                if col not in df.columns:
                    df[col] = None
            df = df[columns]

            # Save in append mode
            file_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(file_path, index=False, mode='a', header=not file_path.exists())
            
            logger.info(f"[{self.store_name}] Successfully saved {len(data_list)} products to {file_path.name}")
        except Exception as e:
            logger.error(f"[{self.store_name}] Critical error saving to CSV: {e}")

    @abc.abstractmethod
    def scrape(self, city, category_url):
        """Main method to be implemented by child classes for store-specific logic."""
        pass
