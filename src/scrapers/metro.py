import json
from datetime import datetime
from loguru import logger

from src.scrapers.base_scraper import BaseScraper
from src.config.settings import METRO_CONFIG

class MetroScraper(BaseScraper):
    def __init__(self):
        super().__init__("Metro")
        self.base_url = METRO_CONFIG["base_api_url"]
        
    def _get_all_category_ids(self) -> list:
        """Fetches Tier 2 category IDs to ensure full coverage without hitting API caps.
        Tier 2 (828 IDs) provides higher granularity than Tier 1 (253) while remaining 
        faster than the micro-level Tier 4 (1,894).
        """
        logger.info(f"[{self.store_name}] Fetching Metro Category Tree (Tier 2 Aisles)...")
        cat_url = f"{self.base_url.replace('/Products', '/Categories')}?type=Categories"
        
        response_text = self.fetch_static(cat_url)
        if not response_text:
            logger.error(f"[{self.store_name}] Failed to fetch category tree.")
            return []
            
        try:
            data = json.loads(response_text)
            categories = data.get("data", [])
            
            # Map out Tier 1 IDs first to identify their children (Tier 2)
            tier1_ids = set(
                cat.get("id") for cat in categories 
                if not cat.get("parent_id") and not cat.get("parentId")
            )
            
            # Tier 2 nodes are those whose parent is a Tier 1 node
            tier2_ids = [
                cat.get("id") for cat in categories 
                if (cat.get("parent_id") or cat.get("parentId")) in tier1_ids
            ]
            
            # Clean list
            tier2_ids = [cid for cid in tier2_ids if cid]
            
            logger.info(f"[{self.store_name}] Identified {len(tier2_ids)} Tier-2 categories for optimal coverage.")
            return tier2_ids
        except json.JSONDecodeError as e:
            logger.error(f"[{self.store_name}] Error parsing category tree: {e}")
            return []

    def scrape(self, city, store_id, max_pages=None):
        logger.info(f"[{self.store_name}] Starting BALANCED-VELOCITY scrape for {city} (StoreID: {store_id})")
        
        # 1. Get Tier 2 IDs for broad yet deep coverage
        category_ids = self._get_all_category_ids()
        if not category_ids:
            logger.error(f"[{self.store_name}] Cannot proceed without categories.")
            return

        total_products_scraped_city = 0
        total_cats = len(category_ids)
        cats_processed = 0

        # 2. Iterate through leaf categories
        for index, cat_id in enumerate(category_ids):
            if max_pages and cats_processed >= max_pages:
                logger.info(f"[{self.store_name}] Reached max category limit, stopping {city}.")
                break
            
            # Simple progress logging every 20 categories or if it actually finds items
            show_progress = (index % 20 == 0) or (index == total_cats - 1)
                
            limit = 100
            offset = 0
            category_total_scraped = 0
            
            while True:
                # Construct API URL securely bypassing the global cap via tier2Id
                url = (
                    f"{self.base_url}"
                    f"?type=Products_nd_associated_Brands"
                    f"&order=product_scoring__DESC"
                    f"&filter=||tier2Id&filterValue=||{cat_id}"
                    f"&offset={offset}"
                    f"&limit={limit}"
                    f"&filter=active&filterValue=true"
                    f"&filter=storeId&filterValue={store_id}"
                    f"&filter=Op.available_stock&filterValue=Op.gt__0&"
                )
                
                response_text = self.fetch_static(url)
                if not response_text:
                    break
                    
                try:
                    data = json.loads(response_text)
                except json.JSONDecodeError:
                    break
                    
                items = data.get("data", [])
                total_cat_count = data.get("total_count", 0)
                
                # If this micro-category is empty for this specific city/store, move on
                if not items:
                    break
                    
                processed_items = []
                now_str = datetime.now().isoformat()
                
                for item in items:
                    price = item.get("sale_price") or item.get("sell_price") or item.get("price")
                    category = item.get("teir1Name") or item.get("tier1Name") or "Unknown"
                    
                    processed_items.append({
                        "store_name": self.store_name,
                        "city": city,
                        "category": category,
                        "product_name": item.get("product_name"),
                        "brand": item.get("brand_name"),
                        "price": price,
                        "quantity": item.get("weight"),
                        "unit": item.get("unit_type"),
                        "image_url": item.get("url"),
                        "product_url": item.get("deep_link"),
                        "scraped_at": now_str
                    })
                    
                # Save just this category's chunks to CSV cleanly
                start_count = len(self.seen_urls)
                self.save_page_to_csv(processed_items, city, "All_Products")
                end_count = len(self.seen_urls)
                
                # Uniqueness delta tracks how many NEW items were added
                new_items_added = end_count - start_count
                
                category_total_scraped += new_items_added
                total_products_scraped_city += new_items_added
                offset += limit
                
                # Safety: If we've hit all items OR if no NEW items were found (indicates loop/redundancy)
                if offset >= total_cat_count or (offset > limit and new_items_added == 0):
                    break
                    
            if category_total_scraped > 0 or show_progress:
                logger.info(f"[{self.store_name}] [{city}] Cat {index+1}/{total_cats} (ID: {cat_id}): Found {category_total_scraped} items. Total: {total_products_scraped_city}")
                
            cats_processed += 1

        logger.info(f"[{self.store_name}] Finished! Extracted {total_products_scraped_city} TOTAL genuine products for {city}.")
