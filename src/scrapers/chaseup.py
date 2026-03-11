import time
import json
import re
from loguru import logger
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from src.scrapers.base_scraper import BaseScraper
from src.config.settings import CHASEUP_CONFIG

class ChaseUpScraper(BaseScraper):
    def __init__(self, city: str):
        super().__init__("Chase Up")
        if city not in CHASEUP_CONFIG["cities"]:
            raise ValueError(f"City '{city}' not configured for Chase Up. Available: {list(CHASEUP_CONFIG['cities'].keys())}")
        
        self.city = city
        self.base_url = CHASEUP_CONFIG["base_api_url"]
        self.headers = CHASEUP_CONFIG["headers"].copy()
        self.city_config = CHASEUP_CONFIG["cities"][city]
        self.categories = CHASEUP_CONFIG.get("categories", ["grocery"])
        
        # Update REST ID in headers to match the city
        self.headers["rest-id"] = self.city_config["restId"]

    def fetch_items(self, keyword: str, page_no: int) -> dict:
        """Fetches products using the search API for a given keyword."""
        import requests
        per_page = 50
        params = {
            "restId": self.city_config["restId"],
            "rest_brId": self.city_config["rest_brId"],
            "delivery_type": "0",
            "source": "",
            "search": keyword, # DEFINITIVE FIX: 'search' instead of 'tag'
            "page_no": str(page_no),
            "per_page": str(per_page),
            "start": str((page_no - 1) * per_page),
            "limit": str(per_page)
        }
        
        # Add branch-specific cookie for stability
        headers = self.headers.copy()
        headers["Cookie"] = f"brId={self.city_config['rest_brId']}"
        headers["Referer"] = "https://www.chaseupgrocery.com/"

        try:
            # Note: base_api_url in settings is already set to search-dish-v2
            response = requests.get(self.base_url, params=params, headers=headers, timeout=30)
            logger.debug(f"[{self.store_name}] Searching Keyword: '{keyword}' (Page {page_no}) | Status: {response.status_code}")
            
            if response.status_code != 200:
                logger.warning(f"[{self.store_name}] Non-200 status for '{keyword}': {response.status_code}")
                return {}
            
            data = response.json()
            data_field = data.get("data", {})
            
            # The API returns results nested under 'dishes' if it's a search result
            if isinstance(data_field, dict):
                items = data_field.get("dishes", [])
            else:
                items = data_field if isinstance(data_field, list) else []

            if not items:
                logger.debug(f"[{self.store_name}] No products in 'dishes' for '{keyword}'. Msg: {data.get('msg')}")
            else:
                logger.info(f"[{self.store_name}] [SUCCESS] Found {len(items)} products for '{keyword}'")
            
            # Return a wrapped dict to keep scrape() consistent
            return {"data": items}
        except Exception as e:
            logger.error(f"[{self.store_name}] Failed to search '{keyword}' page {page_no}: {e}")
            return {}

    def parse_product(self, item: Any, cat_name: str) -> Dict[str, Any]:
        """Extract required fields from a single product JSON node."""
        if not isinstance(item, dict):
            logger.warning(f"[{self.store_name}] Skipping non-dict item: {item} (type: {type(item)})")
            return None

        price = item.get("price")
        if item.get("dish_branch_status") and item["dish_branch_status"].get("price"):
            price = item["dish_branch_status"]["price"]
            
        name = item.get("name", "Unknown Product")
            
        return {
            "store_name": self.store_name,
            "city": self.city,
            "category": cat_name,
            "product_name": name,
            "brand": item.get("brand_name", ""),
            "price": float(price) if price else None,
            "quantity": None, # Will be extracted in Processed Layer (Sec 4.2)
            "unit": None,      # Will be extracted in Processed Layer (Sec 4.2)
            "image_url": item.get("img_url", ""),
            "product_url": None,
            "scraped_at": datetime.now().isoformat()
        }

    def scrape(self, keywords_list: List[str] = None, max_keywords: int = None, max_pages_per_key: int = None):
        """Scrapes Chase Up using a high-density keyword search strategy."""
        logger.info(f"[{self.store_name}] Starting KEYWORD-SEARCH high-yield run for {self.city}")
        
        # Use provided list or default
        keywords = keywords_list if keywords_list else [
            "milk", "dairy", "yogurt", "cheese", "butter", "cream", "eggs", "bread", "rusk", "bun",
            "oil", "ghee", "sugar", "salt", "flour", "atta", "rice", "dal", "pulses", "lentils",
            "tea", "coffee", "juice", "beverage", "drink", "water", "cola", "sprite", "nestle",
            "snacks", "biscuits", "chips", "namkeen", "cake", "chocolate", "candy", "toffee",
            "spices", "masala", "mirch", "haldi", "zeera", "salt", "vinegar", "sauce", "ketchup", "mayo",
            "frozen", "nuggets", "burger", "patty", "pizza", "sausage", "meat", "chicken", "beef",
            "soap", "shampoo", "conditioner", "body wash", "hand wash", "face wash", "lotion", "cream",
            "toothpaste", "toothbrush", "mouthwash", "detergent", "surf", "washing machine", "dishwash",
            "cleaner", "harpic", "phenyl", "insecticide", "mortein", "tissue", "diapers", "baby care",
            "shampoo", "hair care", "cosmetics", "makeup", "perfume", "deodorant",
            "vegetable", "fruit", "potato", "onion", "tomato", "garlic", "ginger", "lemon"
        ]
        
        total_extracted = 0
        total_keywords = len(keywords)
        
        for k_idx, keyword in enumerate(keywords, 1):
            if max_keywords and k_idx > max_keywords:
                logger.info(f"Reached max keywords limit ({max_keywords}). Stopping.")
                break
                
            logger.info(f"[{self.store_name}] [{self.city}] Searching Keyword {k_idx}/{total_keywords}: {keyword}")
            
            page_no = 1
            keyword_total = 0
            while True:
                if max_pages_per_key and page_no > max_pages_per_key:
                    break

                data = self.fetch_items(keyword, page_no)
                items = data.get("data", [])
                if not items:
                    break
                
                processed_items = [self.parse_product(item, keyword) for item in items]
                processed_items = [i for i in processed_items if i is not None]
                
                # Deduplication logic (supports Sec 3.4 city-wise unique rows)
                prev_total = len(self.seen_urls)
                self.save_page_to_csv(processed_items, self.city, keyword)
                new_count = len(self.seen_urls)
                
                actual_new_saved = new_count - prev_total
                keyword_total += actual_new_saved
                total_extracted += actual_new_saved
                
                # Progress logging
                logger.info(f"[{self.store_name}] [{self.city}] '{keyword}' P{page_no} | New: {actual_new_saved} | Total Store: {total_extracted}")
                
                # If we get items but none are new (duplicate page or end of results)
                if actual_new_saved == 0 and page_no > 1:
                    logger.debug(f"Reached end of unique results for '{keyword}' on page {page_no}")
                    break
                    
                page_no += 1
                
        logger.info(f"[{self.store_name}] COMPLETED! Extracted {total_extracted} unique entries for {self.city}.")
                    
        logger.info(f"[{self.store_name}] COMPLETED! Extracted {total_extracted} entries for {self.city}.")

if __name__ == "__main__":
    scraper = ChaseUpScraper(city="Faisalabad")
    # Test run with limits
    scraper.scrape(max_sections=1, max_pages_per_sub=1)
