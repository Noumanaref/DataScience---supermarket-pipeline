import time
import requests
import re
from bs4 import BeautifulSoup
from loguru import logger
from datetime import datetime

from src.scrapers.base_scraper import BaseScraper
from src.config.settings import ALFATAH_CONFIG

class AlFatahScraper(BaseScraper):
    def __init__(self):
        super().__init__(store_name="Al-Fatah")
        self.base_url = ALFATAH_CONFIG["base_url"]
        self.cities = ALFATAH_CONFIG["cities"]
    
    def scrape(self, city: str, category_slug: str, category_name: str, max_pages: int = None) -> bool:
        """
        Scrapes a specific category in a given city from Al-Fatah.
        Uses BeautifulSoup to parse HTML grid-fragments returned by Shopify.
        """
        if city not in self.cities:
            logger.error(f"City '{city}' not found in AlFatah config.")
            return False

        location_id = self.cities[city]
        logger.info(f"Starting Al-Fatah scrape for City: {city} (ID: {location_id}), Collection: {category_name}")

        page = 1
        limit = 80 # Balanced limit for Shopify grid-fragment performance
        total_items_saved = 0
        timestamp = datetime.now().isoformat()
        
        # Al-Fatah (Shopify) blocks fake-useragent strings. Override with modern Chrome.
        custom_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        }

        from src.config.settings import DELAY_BETWEEN_REQUESTS, MAX_RETRIES
        import random

        while True:
            if max_pages and page > max_pages:
                logger.info(f"Reached max pages limit ({max_pages}). Stopping Al-Fatah scrape.")
                break

            # Construct the API URL to get HTML fragments
            url = f"{self.base_url}/collections/{category_slug}?filter.p.m.custom.location_based_availability={location_id}&view=grid-fragment&page={page}&limit={limit}"
            
            logger.debug(f"Fetching Al-Fatah HTML snippet: {url}")
            
            # Using requests directly instead of BaseScraper's fetch_static due to header override restriction
            retries = 0
            html_content = None

            while retries < MAX_RETRIES:
                try:
                    # Sync with global delay settings
                    time.sleep(random.uniform(*DELAY_BETWEEN_REQUESTS))
                    response = requests.get(url, headers=custom_headers, timeout=30)
                    response.raise_for_status()
                    html_content = response.text
                    break
                except Exception as e:
                    retries += 1
                    logger.warning(f"Error fetching Al-Fatah (attempt {retries}): {url} - {e}")
                    time.sleep(2 ** retries)
            
            if not html_content:
                logger.error(f"Failed to fetch Al-Fatah data for {category_slug} (Page {page}).")
                break
                
            soup = BeautifulSoup(html_content, 'html.parser')
            product_cards = soup.select('.product-card')
            
            if not product_cards:
                logger.info(f"No more products found on page {page}. Scraping finished for {category_slug}.")
                break
                
            logger.info(f"Page {page}: Parsing {len(product_cards)} products... [Cumulative Saved: {total_items_saved}]")
            
            data_to_save = []
            new_unique_found = False
            
            for index, card in enumerate(product_cards):
                try:
                    # 1. Product Name
                    title_elem = card.select_one('.product-title-ellipsis')
                    product_name = title_elem.text.strip() if title_elem else "Unknown Product"
                    
                    # 2. Product URL
                    product_rel_url = title_elem['href'] if title_elem and title_elem.has_attr('href') else ""
                    product_url = f"{self.base_url}{product_rel_url}" if product_rel_url else "N/A"
                    
                    # Track uniqueness via the new BaseScraper guard
                    if product_url in self.seen_urls and product_url != "N/A":
                        continue
                    
                    new_unique_found = True

                    # 3. Image URL
                    img_elem = card.select_one('.product-image img')
                    image_url = img_elem['src'] if img_elem and img_elem.has_attr('src') else "N/A"
                    if image_url.startswith('//'):
                        image_url = "https:" + image_url
                        
                    # 4. Price
                    price_elem = card.select_one('.product-price span')
                    # Cleaning price: "Rs.275.00" -> "275.00"
                    price_str = price_elem.text.strip() if price_elem else "0.0"
                    price_str = price_str.replace('Rs.', '').replace(',', '').strip()
                    try:
                        price = float(price_str)
                    except ValueError:
                        price = 0.0

                    brand = "N/A" 
                    
                    data_to_save.append({
                        "store_name": "Al-Fatah",
                        "city": city,
                        "category": category_name,
                        "product_name": product_name,
                        "brand": brand,
                        "price": price,
                        "quantity": None, # Will be extracted in Processed Layer (Sec 4.2)
                        "unit": None,     # Will be extracted in Processed Layer (Sec 4.2)
                        "image_url": image_url,
                        "product_url": product_url,
                        "scraped_at": timestamp
                    })
                except Exception as e:
                    logger.warning(f"Error parsing product card at index {index} on page {page}: {e}")
                    continue
            
            # If an entire page yielded NO new products, we have reached the end/loop
            if not new_unique_found and product_cards:
                logger.info(f"No new unique products found on page {page} (Loop detected). Scraping finished.")
                break

            if data_to_save:
                self.save_page_to_csv(
                    data_list=data_to_save,
                    city=city,
                    category=category_name
                )
                total_items_saved += len(data_to_save)
                
            page += 1

        logger.success(f"Successfully saved {total_items_saved} items for Al-Fatah {city} - {category_name}.")
        return total_items_saved > 0

if __name__ == "__main__":
    scraper = AlFatahScraper()
    # Test with the verified whale collection
    scraper.scrape("Lahore", "active-items", "All Products")
