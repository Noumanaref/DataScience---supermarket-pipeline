import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for folder in [RAW_DATA_DIR, PROCESSED_DATA_DIR, LOGS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Database settings
DB_PATH = DATA_DIR / "supermarket_pipeline.db"

# Scraper Settings
TIMEOUT = 30
MAX_RETRIES = 3
DELAY_BETWEEN_REQUESTS = (0.5, 1.5)

# Store API Configurations
METRO_CONFIG = {
    "base_api_url": "https://admin.metro-online.pk/api/read/Products",
    "cities": {
        "Faisalabad": 15, "Lahore Airport": 16, "Lahore Thokar Niaz Baig": 10,
        "Karachi Safari": 12, "Karachi Manghopir": 22, "Karachi Stargate": 23,
        "Islamabad": 11, "Multan": 14
    }
}

ALFATAH_CONFIG = {
    "base_url": "https://alfatah.pk",
    "cities": {
        "Sialkot": "93608968480", "Islamabad": "93608837408", "Lahore": "93608247584",
        "Faisalabad": "93608444192", "Gujranwala": "93608771872"
    },
    "categories": ["grocery-staples", "beverages", "health-beauty"]
}

CHASEUP_CONFIG = {
    "base_api_url": "https://www.chaseupgrocery.com/api/search-dish-v2",
    "headers": {
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/145.0.0.0 Safari/537.36"
    },
    "cities": {
        "Faisalabad": {"restId": "55525", "rest_brId": "56249"},
        "Karachi Sea View": {"restId": "55525", "rest_brId": "56246"},
        "Karachi Abbasi Shaheed Road": {"restId": "55525", "rest_brId": "56247"}
    }
}
