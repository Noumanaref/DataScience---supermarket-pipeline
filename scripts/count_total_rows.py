import glob
import pandas as pd
from pathlib import Path

raw_dir = Path(r'd:\supermarket-pipeline\data\raw')
files = list(raw_dir.glob('*.csv'))

total_rows = 0
for f in files:
    try:
        # Just head the file to get columns then use wc or similar if needed, 
        # but for accuracy we count properly.
        df = pd.read_csv(f, usecols=[0], low_memory=False, on_bad_lines='skip')
        total_rows += len(df)
    except Exception as e:
        continue

print(f"TOTAL_RAW_ROWS: {total_rows}")
