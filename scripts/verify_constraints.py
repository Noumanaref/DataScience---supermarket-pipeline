import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path(r'd:\supermarket-pipeline')
PROCESSED_DATA = BASE_DIR / 'data' / 'processed' / 'cleaned_data_full.csv'
MATCHED_DATA   = BASE_DIR / 'data' / 'matched' / 'matched_products.csv'

def verify():
    print("="*50)
    print("      SUPERMARKET PIPELINE VERIFICATION")
    print("="*50)
    
    # 1. Cleaned Rows (Pandas DataFrame)
    if PROCESSED_DATA.exists():
        df_clean = pd.read_csv(PROCESSED_DATA, low_memory=False)
        rows = len(df_clean)
        print(f"[OK] Cleaned Rows: {rows:,}")
        
        # 2. Chains & Cities
        chains = df_clean['store_name'].unique()
        cities = df_clean['city'].unique()
        print(f"[OK] Chains ({len(chains)}): {', '.join(chains)}")
        print(f"[OK] Cities ({len(cities)}): {', '.join(cities)}")
        
        # City per chain breakdown
        for chain in chains:
            c_cities = df_clean[df_clean['store_name'] == chain]['city'].unique()
            print(f"   - {chain}: {len(c_cities)} cities ({', '.join(c_cities)})")
    else:
        print("[FAIL] Processed data file not found!")

    # 3. Matched Products
    if MATCHED_DATA.exists():
        df_match = pd.read_csv(MATCHED_DATA, low_memory=False)
        matches = df_match['product_id'].nunique()
        print(f"[OK] Matched Products: {matches:,}")
    else:
        print("[FAIL] Matched data file not found!")

    print("="*50)

if __name__ == "__main__":
    verify()
