from src.scrapers.metro import MetroScraper
from src.scrapers.alfatah import AlFatahScraper
from src.scrapers.chaseup import ChaseUpScraper
from src.config.settings import METRO_CONFIG, ALFATAH_CONFIG, CHASEUP_CONFIG
from loguru import logger

def main():
    logger.info("Starting Supermarket Pipeline Data Collection")
    
    # Run Al-Fatah Scraper (EXPANDED YIELD - PHASE 2)
    logger.info("Starting Al-Fatah (EXPANDED YIELD PHASE 2)")
    alfatah_scraper = AlFatahScraper()
    for city in ALFATAH_CONFIG["cities"].keys():
        alfatah_scraper.reset_unique_guard()
        for category_slug in ALFATAH_CONFIG["categories"]:
            alfatah_scraper.scrape(city=city, category_slug=category_slug, category_name=category_slug)

    # Run Chase Up Scraper (EXPANDED YIELD - PHASE 2)
    logger.info("Starting Chase Up (HIGH-YIELD KEYWORD RECOVERY PHASE 2)")
    from config.chaseup_keywords import CHASEUP_KEYWORDS
    for city in CHASEUP_CONFIG["cities"].keys():
        chaseup_scraper = ChaseUpScraper(city=city)
        chaseup_scraper.reset_unique_guard()
        chaseup_scraper.scrape(keywords_list=CHASEUP_KEYWORDS)

if __name__ == "__main__":
    main()
