"""
Layer 3: Data Normalization
===========================
Steps 3.1 - 3.5 from Layer_by_Layer.md:
  3.1 Unit Standardization  (kg<->g, L<->ml, dozen<->pieces)
  3.2 Brand Extraction       (predefined list + regex caps)
  3.3 Price-Per-Unit         (price / normalized_quantity)
  3.4 Category Normalization (synonym collapse)
  3.5 Save normalized_data.csv
"""

import pandas as pd
import re
import numpy as np
from pathlib import Path
from loguru import logger
from src.config.settings import PROCESSED_DATA_DIR

INPUT_PATH  = PROCESSED_DATA_DIR / "cleaned_data.csv"
OUTPUT_PATH = PROCESSED_DATA_DIR / "normalized_data.csv"

# ---------------------------------------------------------------------------
# 3.1  Unit Standardization helpers
# ---------------------------------------------------------------------------
# We store everything in BASE units:  WEIGHT -> grams,  VOLUME -> millilitres
UNIT_TO_GRAMS = {
    "kg": 1000, "g": 1, "gram": 1, "grams": 1,
    "lb": 453.592, "oz": 28.3495,
}
UNIT_TO_ML = {
    "l": 1000, "ltr": 1000, "liter": 1000, "litre": 1000,
    "ml": 1, "millilitre": 1, "milliliter": 1,
}
UNIT_PIECES = {
    "dozen": 12, "dz": 12,
    "pcs": 1, "pc": 1, "pack": 1, "pk": 1, "packets": 1,
    "sachet": 1, "can": 1, "bottle": 1, "tub": 1, "box": 1,
    "eggs": 1, "extract": 1,
}

def standardize_unit(size_val, unit_raw):
    """Returns (normalized_qty, base_unit)  e.g.  (500, 'ml') or (1000, 'g')."""
    if pd.isna(size_val) or pd.isna(unit_raw):
        return None, "N/A"

    val  = float(size_val)
    unit = str(unit_raw).lower().strip()

    if unit in UNIT_TO_GRAMS:
        return round(val * UNIT_TO_GRAMS[unit], 4), "g"
    if unit in UNIT_TO_ML:
        return round(val * UNIT_TO_ML[unit], 4), "ml"
    if unit in UNIT_PIECES:
        return round(val * UNIT_PIECES[unit], 4), "pcs"

    return val, unit  # unchanged if unknown

# ---------------------------------------------------------------------------
# 3.2  Brand Extraction
# ---------------------------------------------------------------------------
KNOWN_BRANDS = [
    "Nestle", "National", "Shan", "Rafhan", "Knorr", "Mitchells", "Olpers",
    "MilkPak", "Comelle", "Nurpur", "Dalda", "Sufi", "Habib", "Mezan",
    "Tullo", "Vital", "Tapal", "Lipton", "Supreme", "Pepsi", "Coke",
    "7up", "Dew", "Pakola", "Rooh Afza", "Hamdard", "Qarshi", "LU", "EBM",
    "Peak Freans", "Prince", "Oreo", "Tiger", "Gala", "Sooper", "Lays",
    "Kurkure", "Cheetos", "Kolson", "Bake Parlor", "Youngs", "Shangrila",
    "Lux", "Lifebuoy", "Sunsilk", "Pantene", "Dove", "Palmolive", "Loreal",
    "Colgate", "Sensodyne", "Dettol", "SafeGuard", "Gillette", "Surf",
    "Ariel", "Bonus", "Brite", "Lemon Max", "Vim", "Rose Petal", "Tulip",
    "Always", "Kotex", "Pampers", "Molfix", "Canbebe", "Johnson",
    "Nivea", "Ponds", "Olay", "Glow & Lovely", "Fair & Lovely",
    "Horlicks", "Complan", "Milo", "Ensure", "Pediasure", "Cerelac",
    "Lactogen", "Tang", "Blue Band", "Red Bull", "Sting", "Aquafina",
    "Mehran", "Kitchen King", "Laziza", "Fauji", "Eva",
]
# Lowercase lookup for fast matching
KNOWN_BRANDS_LOWER = {b.lower(): b for b in KNOWN_BRANDS}

def extract_brand(product_name, existing_brand):
    """Return brand from known list, then regex CAPITALS, else existing field."""
    if not pd.isna(existing_brand) and str(existing_brand).strip().lower() not in ("n/a", "nan", ""):
        return str(existing_brand).strip()

    name_lower = str(product_name).lower()
    for lbrand, proper in KNOWN_BRANDS_LOWER.items():
        if lbrand in name_lower:
            return proper

    # Fallback: first capitalised token
    caps = re.findall(r'\b[A-Z][a-z]+\b', str(product_name))
    return caps[0] if caps else "Unknown"

# ---------------------------------------------------------------------------
# 3.4  Category Normalization
# ---------------------------------------------------------------------------
CATEGORY_MAP = {
    # Dairy
    "dairy": "Dairy", "dairy-products": "Dairy", "breakfast-dairy": "Dairy",
    "milk": "Dairy", "cheese": "Dairy", "yogurt": "Dairy", "butter": "Dairy",
    # Beverages
    "beverages": "Beverages", "drinks": "Beverages", "juice": "Beverages",
    "beverage": "Beverages", "tea": "Beverages", "coffee": "Beverages",
    # Grocery / Staples
    "grocery": "Grocery Staples", "grocery-staples": "Grocery Staples",
    "baking-cooking": "Grocery Staples", "spices-recipes": "Grocery Staples",
    "noodles-ketchups": "Grocery Staples", "canned-jar-food": "Grocery Staples",
    "active-items": "Grocery Staples",
    # Snacks
    "biscuits-snacks-chocolates": "Snacks & Confectionery",
    "snacks": "Snacks & Confectionery", "biscuit": "Snacks & Confectionery",
    "chocolate": "Snacks & Confectionery", "candy": "Snacks & Confectionery",
    # Frozen / Meat
    "frozen": "Frozen & Meat", "meat-price-in-pakistan": "Frozen & Meat",
    "meat-poultry": "Frozen & Meat",
    # Personal Care
    "health-beauty": "Personal Care", "personal-care": "Personal Care",
    "bath-body": "Personal Care", "hair-care": "Personal Care",
    "skin-care": "Personal Care", "oral-care": "Personal Care",
    # Household
    "laundry-household": "Household", "household-needs": "Household",
    "cleaning-tools": "Household", "household-plastics": "Household",
    # Baby
    "baby-care": "Baby Care",
    # Baby / Others
    "bakery": "Bakery", "stationery": "Stationery", "pet-care": "Pet Care",
}

def normalize_category(cat):
    if pd.isna(cat): return "Other"
    return CATEGORY_MAP.get(str(cat).strip().lower(), str(cat).strip().title())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def normalize():
    logger.info("Starting Layer 3: Data Normalization")

    from src.config.settings import DATA_DIR, PROCESSED_DATA_DIR
    STAGING_DIR = DATA_DIR / "staging"

    # Load staging files and inject store_name from filename
    # Staging filenames follow: StoreName_City_MASTER.csv
    staging_files = list(STAGING_DIR.glob("*_MASTER.csv"))
    if not staging_files:
        logger.error("No staging files found. Run consolidation first.")
        return

    all_dfs = []
    for f in staging_files:
        try:
            temp_df = pd.read_csv(f, low_memory=False)
            # Inject store_name from filename if not already present
            if "store_name" not in temp_df.columns:
                parts = f.stem.split("_")
                # Pattern: StoreName_City_MASTER → store is everything before City token
                # E.g. "Al-Fatah_Lahore_MASTER" → "Al-Fatah", "Chase Up_Karachi Sea View_MASTER"
                # The last part is "MASTER", second-to-last is city, everything before is store
                store_name = parts[0]  # First token is always the store name
                temp_df["store_name"] = store_name
            all_dfs.append(temp_df)
        except Exception as e:
            logger.error(f"Error reading {f.name}: {e}")

    df = pd.concat(all_dfs, ignore_index=True)

    # Apply price cleaning from processor to get price_clean if not already done
    if "price_clean" not in df.columns:
        import re
        def clean_price(price):
            if pd.isna(price): return 0.0
            price_str = re.sub(r'rs\.?|pkr|[\,]', '', str(price).lower()).strip()
            try: return float(price_str)
            except: return 0.0
        df["price_clean"] = df["price"].apply(clean_price)
        df["product_name_clean"] = df["product_name"].str.lower().str.strip()

    # If extracted_size / extracted_unit not in df from cleaned_data, extract now
    if "extracted_size" not in df.columns:
        import re as _re
        UNIT_PAT = r'(\d+(?:\.\d+)?)\s*(kg|g|gram|ltr|l|liter|ml|millilitre|oz|lb|pcs|pc|pack|packets|sachet|can|bottle|tub|box)'
        def _extract(row):
            text = f"{str(row.get('product_name',''))} {str(row.get('quantity',''))}".lower()
            if "half kg" in text: return 0.5, "kg"
            m = _re.search(UNIT_PAT, text)
            if m: return float(m.group(1)), m.group(2)
            return None, "N/A"
        extracted = df.apply(_extract, axis=1)
        df["extracted_size"] = [x[0] for x in extracted]
        df["extracted_unit"] = [x[1] for x in extracted]

    logger.info(f"Loaded {len(df)} staged rows.")

    # 3.1 Unit Standardization
    logger.info("Step 3.1: Standardizing units...")
    std = df.apply(
        lambda r: standardize_unit(r.get("extracted_size"), r.get("extracted_unit")),
        axis=1
    )
    df["size_normalized"]  = [x[0] for x in std]
    df["unit_normalized"]  = [x[1] for x in std]

    # 3.2 Brand Extraction
    logger.info("Step 3.2: Extracting brands...")
    df["brand_clean"] = df.apply(
        lambda r: extract_brand(r.get("product_name", ""), r.get("brand", "")),
        axis=1
    )

    # 3.3 Price-Per-Unit
    logger.info("Step 3.3: Calculating Price-Per-Unit...")
    def calc_ppu(row):
        price = row.get("price_clean", 0)
        qty   = row.get("size_normalized")
        unit  = row.get("unit_normalized", "N/A")
        if pd.isna(qty) or qty == 0 or unit == "N/A":
            return None
        # PPU is always price per base unit (per gram, per ml)
        return round(float(price) / float(qty), 6)

    df["price_per_unit"] = df.apply(calc_ppu, axis=1)

    # 3.4 Category Normalization
    logger.info("Step 3.4: Normalizing categories...")
    df["category_normalized"] = df["category"].apply(normalize_category)

    # 3.5 Save
    output_cols = [
        "store_name", "city",
        "product_name_clean", "brand_clean",
        "price_clean", "size_normalized", "unit_normalized", "price_per_unit",
        "category_normalized",
        "image_url", "product_url", "scraped_at",
    ]
    # Keep only cols that exist in df
    output_cols = [c for c in output_cols if c in df.columns]
    df[output_cols].to_csv(OUTPUT_PATH, index=False)

    ppu_coverage = df["price_per_unit"].notna().mean() * 100
    logger.success(
        f"Normalization complete. "
        f"{len(df)} rows → {OUTPUT_PATH.name} | "
        f"PPU coverage: {ppu_coverage:.1f}%"
    )
    return df


if __name__ == "__main__":
    normalize()
