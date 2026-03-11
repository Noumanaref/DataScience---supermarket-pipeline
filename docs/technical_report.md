# Technical Report: Large-Scale Supermarket Price Index Pipeline

## 1. Executive Summary
This project implements an end-to-end data engineering and analytics pipeline to monitor price wars across major Pakistani supermarket chains. By scraping over 500,000 raw data points and applying advanced entity resolution, we have constructed a high-resolution Price Index covering 16 cities and 3 major retailers.

## 2. Architecture & Data Flow
The system is built as a modular "Layer-by-Layer" pipeline:
- **Layer 1 (Collection)**: Autonomous scrapers for Metro, Al-Fatah, and Chase Up.
- **Layer 2 (Cleaning)**: Regex-based size extraction and multi-stage outlier detection.
- **Layer 3 (Normalization)**: Unit standardization (g/ml) and brand extraction for 50+ known players.
- **Layer 4 (Entity Resolution)**: Bayesian-inspired fuzzy matching using `rapidfuzz` to align products across retailers.
- **Layer 5-9 (Analytics)**: Computation of LDI, CV, Spearman correlations, and hierarchical clustering.

## 3. Detailed Scraping Strategy
The data collection layer was designed for robustness and high yield across heterogeneous web architectures.

### 3.1. Global Infrastructure (`BaseScraper`)
All scrapers share a foundational class that enforces:
- **Anti-Detection**: `fake-useragent` header rotation and randomized delays.
- **Robustness**: Exponential backoff (up to 5 attempts) for network errors.
- **Uniqueness Guard**: Memory-based `seen_urls` tracking to prevent city-level duplicates.

### 3.2. Store-Specific Implementations
| Store | Technical Strategy | Key Nuance |
| :--- | :--- | :--- |
| **Metro** | **API Tier-2 Traversal** | Bypassed global 1000-item caps by targeting Tier 2 categories (Aisles). |
| **Chase Up** | **Keyword-Density Search** | Injected 100+ grocery keywords into the search-dish-v2 API with branch-specific `rest-id` headers. |
| **Al-Fatah** | **Shopify Fragment Parsing** | Targeted `grid-fragment` views for optimized HTML snippets, using Chrome fingerprinting to evade bots. |

### 3.3. Engineering Challenges
- **Loop Protection**: Implemented "New Item Delta" checks to terminate pagination when redundant data is detected.
- **Bot Mitigation**: Overrode generic library headers with modern Chrome identifiers for Shopify-based targets.

## 4. Entity Resolution & Data Alignment
To handle "Product Identity Uncertainty," we developed a token-based fuzzy matching algorithm:
- **Grouping**: Brand + Size ± 5% tolerance.
- **Scoring**: Levenshtein distance on product name tokens (Threshold: 80).
- **Result**: Successfully aligned 11,561 grocery records into 730 distinct product cohorts.

---
*Report Generated: 2026-03-11*
*Total Verified Rows: 638,623*
