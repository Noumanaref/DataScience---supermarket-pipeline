import pandas as pd
import re
import numpy as np
from pathlib import Path
from loguru import logger
from datetime import datetime
from src.config.settings import DATA_DIR, PROCESSED_DATA_DIR

# Staging directory from Layer 1.5
STAGING_DIR = DATA_DIR / "staging"

class DataProcessor:
    def __init__(self):
        self.output_path = PROCESSED_DATA_DIR / "cleaned_data.csv"
        
        # Regex patterns for unit extraction
        # Matches patterns like "500g", "1.5 kg", "250 ml", "1 liter", "pack of 6", etc.
        self.unit_patterns = [
            r'(\d+(?:\.\d+)?)\s*(kg|g|gram|kg|ltr|l|liter|ml|millilitre|oz|lb|pcs|pc|pack|packets|eggs|dozen|extract|can|bottle|sachet|tub|box|pk)',
        ]

    def clean_name(self, name):
        """Step 2.3: Clean product names"""
        if pd.isna(name): return "N/A"
        name = str(name).lower()
        name = re.sub(r'[^\w\s\.\-\/]', '', name) # Remove special chars except . - /
        name = " ".join(name.split()) # Standardize whitespace
        return name

    def clean_price(self, price):
        """Step 2.3: Clean prices"""
        if pd.isna(price): return 0.0
        # Remove Rs., PKR, commas, etc.
        price_str = str(price).lower()
        price_str = re.sub(r'rs\.?|pkr|[\,]', '', price_str).strip()
        try:
            return float(price_str)
        except:
            return 0.0

    def extract_size_unit(self, name, size_field):
        """Step 2.3: Extract numeric values and units (regex)"""
        text_to_search = f"{str(name)} {str(size_field)}".lower()
        
        # Handle "half kg" case explicitly as requested
        if "half kg" in text_to_search:
            return 0.5, "kg"
        if "quarter kg" in text_to_search:
            return 0.25, "kg"

        for pattern in self.unit_patterns:
            match = re.search(pattern, text_to_search)
            if match:
                val = float(match.group(1))
                unit = match.group(2)
                return val, unit
                
        return None, "N/A"

    def process(self):
        logger.info("Starting Milestone 2: Data Cleaning & Validation (Layer 2)")
        
        # Step 2.1: Data Loading
        staged_files = list(STAGING_DIR.glob("*.csv"))
        if not staged_files:
            logger.error("No staged files found in data/staging. Run consolidation first.")
            return

        all_dfs = []
        for f in staged_files:
            all_dfs.append(pd.read_csv(f))
        
        df = pd.concat(all_dfs, ignore_index=True)
        logger.info(f"Loaded {len(df)} records from Staging.")

        # Step 2.2: Validation Checks (Before cleaning)
        logger.info("Performing Validation Checks...")
        
        # 1. Null Check
        null_report = df.isnull().mean() * 100
        logger.info(f"Missing Values Check (%):\n{null_report[null_report > 0]}")

        # Step 2.3: Cleaning Steps
        logger.info("Executing Cleaning & Extraction Logic...")
        
        # Name and Price
        df['product_name_clean'] = df['product_name'].apply(self.clean_name)
        df['price_clean'] = df['price'].apply(self.clean_price)
        
        # Size and Unit Extraction
        extracted = df.apply(lambda row: self.extract_size_unit(row['product_name'], row['quantity']), axis=1)
        df['extracted_size'] = [x[0] for x in extracted]
        df['extracted_unit'] = [x[1] for x in extracted]

        # Step 2.2: Price Sanity & Outlier Detection
        initial_count = len(df)
        
        # Price > 0 and < 1,000,000
        df = df[(df['price_clean'] > 0) & (df['price_clean'] < 1000000)]
        
        # IQR Outlier Detection for Prices (per Store)
        def remove_price_outliers(group):
            Q1 = group['price_clean'].quantile(0.25)
            Q3 = group['price_clean'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return group[(group['price_clean'] >= lower_bound) & (group['price_clean'] <= upper_bound)]

        df = df.groupby('store_name', group_keys=False).apply(remove_price_outliers)
        
        final_count = len(df)
        logger.info(f"Validation complete. Removed {initial_count - final_count} invalid/outlier rows.")

        # Step 2.4: Save Cleaned Data
        df.to_csv(self.output_path, index=False)
        logger.success(f"Successfully saved {len(df)} cleaned rows to {self.output_path}")
        
        return df

if __name__ == "__main__":
    processor = DataProcessor()
    processor.process()
