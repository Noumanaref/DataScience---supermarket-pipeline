import pandas as pd
from pathlib import Path
from loguru import logger
from datetime import datetime
from config.settings import RAW_DATA_DIR, DATA_DIR

# Define staging directory
STAGING_DIR = DATA_DIR / "staging"
STAGING_DIR.mkdir(parents=True, exist_ok=True)

def consolidate():
    """
    Consolidates 925 fragmented CSVs into master Store-City files.
    Ensures global deduplication within each city branch.
    """
    logger.info("Starting Data Consolidation (Layer 1.5)")
    
    # 1. Group files by (Store, City)
    raw_files = list(RAW_DATA_DIR.glob("*.csv"))
    groups = {}
    
    for file_path in raw_files:
        # Pattern: StoreName_City_Category_Date.csv
        parts = file_path.stem.split("_")
        if len(parts) >= 3:
            store = parts[0]
            city = parts[1]
            key = (store, city)
            
            if key not in groups:
                groups[key] = []
            groups[key].append(file_path)

    total_consolidated_rows = 0
    
    # 2. Process each Group
    for (store, city), files in groups.items():
        logger.info(f"Consolidating {len(files)} files for {store} - {city}...")
        
        all_dfs = []
        for f in files:
            try:
                df = pd.read_csv(f)
                if not df.empty:
                    all_dfs.append(df)
            except Exception as e:
                logger.error(f"Error reading {f.name}: {e}")
        
        if not all_dfs:
            continue
            
        # Merge all categories/keywords into one master City DF
        master_df = pd.concat(all_dfs, ignore_index=True)
        
        # Deduplication logic (Global check per Store-City)
        # We use product_url if available, else name+price
        initial_len = len(master_df)
        
        # Create a unique key for deduplication
        master_df['dedupe_key'] = master_df['product_url'].fillna('') + master_df['product_name'].fillna('') + master_df['price'].astype(str)
        
        master_df = master_df.drop_duplicates(subset=['dedupe_key'])
        master_df = master_df.drop(columns=['dedupe_key'])
        
        final_len = len(master_df)
        removed = initial_len - final_len
        total_consolidated_rows += final_len
        
        # Save to staging
        output_name = f"{store}_{city}_MASTER.csv"
        output_path = STAGING_DIR / output_name
        master_df.to_csv(output_path, index=False)
        
        logger.success(f"Saved {final_len} unique items to {output_name} (Removed {removed} duplicates)")

    logger.info(f"Consolidation Complete. Total Staged Rows: {total_consolidated_rows}")
    return total_consolidated_rows

if __name__ == "__main__":
    consolidate()
