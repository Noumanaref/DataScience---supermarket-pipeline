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
DELAY_BETWEEN_REQUESTS = (0.5, 1.5) # (min, max) seconds

# Store API Configurations
METRO_CONFIG = {
    "base_api_url": "https://admin.metro-online.pk/api/read/Products",
    "cities": {
        "Faisalabad": 15,
        "Lahore Airport": 16,
        "Lahore Thokar Niaz Baig": 10,
        "Karachi Safari": 12,
        "Karachi Manghopir": 22,
        "Karachi Stargate": 23,
        "Islamabad": 11,
        "Multan": 14
    }
}

ALFATAH_CONFIG = {
    "base_url": "https://alfatah.pk",
    "cities": {
        "Sialkot": "93608968480",
        "Islamabad": "93608837408",
        "Lahore": "93608247584",  
        "Faisalabad": "93608444192",
        "Gujranwala": "93608771872"
    },
    "categories": [
        "active-items", "grocery-staples", "beverages", "biscuits-snacks-chocolates", 
        "breakfast-dairy", "frozen", "laundry-household", "noodles-ketchups",
        "baby-care", "health-beauty", "baking-cooking", "stationery", "pet-care",
        "meat-price-in-pakistan", "bakery", "personal-care", "household-needs",
        "canned-jar-food", "spices-recipes", "cleaning-tools", "car-care",
        "bakery", "dairy-products", "meat-poultry", "fresh-vegetables-fruits",
        "sauces-pickles-chutneys", "sweets-salts", "health-wellness", "party-needs",
        "household-plastics", "kitchen-accessories", "disposables", "electrical-items",
        "bath-body", "hair-care", "skin-care", "oral-care", "men-care", "woman-care",
        "kids-toys", "sports-fitness", "mobile-accessories", "computer-laptop-accessories",
        "gift-sets", "perfumes-deodorants", "imported-items", "luxury-items"
    ]
}

CHASEUP_CONFIG = {
    "base_api_url": "https://www.chaseupgrocery.com/api/search-dish-v2",
    "menu_api_url": "https://www.chaseupgrocery.com/api/menu-section",
    "sub_section_api_url": "https://www.chaseupgrocery.com/api/sub-section",
    "items_api_url": "https://www.chaseupgrocery.com/api/items-by-subsection",
    "headers": {
        "accept": "application/json, text/plain, */*",
        "app-name": "chaseup",
        "timezone": "Asia/Karachi",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
    },
    "cities": {
        "Faisalabad": {"restId": "55525", "rest_brId": "56249"},
        "Karachi Shaheed-e-Millat": {"restId": "55525", "rest_brId": "104724"},
        "Karachi Sea View": {"restId": "55525", "rest_brId": "56246"},
        "Karachi Abbasi Shaheed Road": {"restId": "55525", "rest_brId": "56247"},
        "Karachi Gulshan-e-Iqbal": {"restId": "55525", "rest_brId": "56119"},
        "Multan": {"restId": "55525", "rest_brId": "56248"},
        "Gujranwala": {"restId": "55525", "rest_brId": "56250"},
        "Hyderabad": {"restId": "55525", "rest_brId": "58565"}
    },
    "categories": [
        "grocery", "food", "milk", "tea", "coffee", "biscuit", "cake", "oil", "ghee", "rice",
        "sugar", "salt", "spice", "daal", "flour", "atta", "meat", "chicken", "beef", "fish",
        "frozen", "cheese", "butter", "yogurt", "bread", "egg", "noodle", "pasta", "sauce",
        "ketchup", "jam", "honey", "chocolate", "candy", "chips", "snack", "vegetable", "fruit",
        "dry fruit", "nuts", "dates", "shampoo", "soap", "lotion", "cream", "powder", "detergent",
        "cleaner", "tissue", "diaper", "perfume", "deodorant", "juice", "drink", "water",
        "toothpaste", "brush", "hair", "body wash", "hand wash", "sanitizer", "mask",
        "electronics", "appliance", "mobile", "charger", "cable", "headphone", "earphone",
        "speaker", "watch", "smartwatch", "tv", "iron", "blender", "mixer", "microwave",
        "fridge", "freezer", "ac", "fan", "heater", "fashion", "clothing", "shirt", "pant",
        "kurta", "shalwar", "kameez", "dress", "suit", "jacket", "sweater", "coat", "tie",
        "shoes", "sneaker", "sandal", "slipper", "boot", "bag", "purse", "wallet", "belt",
        "toy", "game", "doll", "car", "puzzle", "board", "sports", "ball", "bat", "racket",
        "fitness", "gym", "dumbell", "mat", "treadmill", "health", "beauty", "cosmetic",
        "makeup", "lipstick", "nail", "foundation", "kitchen", "cookware", "pot", "pan",
        "plate", "bowl", "glass", "cup", "mug", "spoon", "fork", "knife", "dining",
        "furniture", "bed", "sofa", "chair", "table", "desk", "closet", "cabinet", "shelf",
        "decor", "carpet", "rug", "curtain", "lamp", "clock", "mirror", "bedding", "pillow",
        "blanket", "sheet", "towel", "bath", "stationery", "pen", "pencil", "notebook",
        "paper", "file", "folder", "book", "magazine", "novel", "outdoor", "garden", "plant",
        "pot", "seed", "tool", "hardware", "drill", "hammer", "screwdriver", "wrench",
        "plier", "nail", "screw", "paint", "brush", "roller", "tape", "glue", "pet",
        "dog", "cat", "bird", "fish", "food", "toy", "bed", "collar", "leash", "auto",
        "car", "bike", "motorcycle", "part", "accessory", "tire", "oil", "battery",
        "wash", "wax", "polish"
    ]
}
