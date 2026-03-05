# Supermarket Data Pipeline

A modular data engineering pipeline for scraping and matching product data from various supermarkets (Metro, Imtiaz, Alfatah).

## Structure
- `scrapers/`: Scraper logic using inheritance from `BaseScraper`.
- `data/`: Data storage divided into `raw`, `processed`, and `matched`.
- `config/`: Pipeline configuration.
- `logs/`: Traceability and audit logs.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the pipeline:
   ```bash
   python main.py
   ```
