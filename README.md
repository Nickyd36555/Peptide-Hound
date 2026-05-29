# Peptide Hound 🐕

A price comparison tool for research peptide vendors. Scrapes product listings from 6 vendors and displays them sorted by price-per-mg so you can instantly find the best deal.

## Vendors tracked

| Vendor | Scraper type |
|--------|-------------|
| Peptide Sciences | WooCommerce HTML |
| Limitless Life | WooCommerce HTML |
| Amino Asylum | Shopify `/products.json` API |
| Pure Rawz | WooCommerce HTML |
| Behemoth Labz | WooCommerce HTML |
| Swiss Chems | WooCommerce HTML |

## Quick start

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Then open **http://localhost:8000**

The database seeds with sample pricing data on the first run so the UI works immediately. Click **Refresh Prices** to trigger a live scrape.

## API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/products` | All peptides grouped by name, sorted by cheapest $/mg |
| `GET` | `/api/products/{name}` | All vendor listings for a specific peptide |
| `POST` | `/api/scrape` | Trigger a full rescrape of all vendors |
| `GET` | `/api/health` | Health check |

## Project structure

```
backend/
  main.py          FastAPI app, API endpoints, scrape runner
  database.py      SQLAlchemy models (SQLite)
  normalizer.py    Canonical name mapping (BPC-157 / BPC157 / BPC 157 → BPC-157)
  scrapers/
    base.py        BaseScraper ABC + shared utilities
    *.py           One scraper per vendor
frontend/
  index.html       Single-page app
  style.css        Dark theme
  app.js           Vanilla JS — fetch, render, sort, search
requirements.txt
```

## Notes

- Scrapers handle failure gracefully — one broken vendor does not crash the rest.
- Weight is extracted from product names (e.g. "BPC-157 **5mg**"). Products without a parseable weight are skipped.
- `price_per_mg` is the primary comparison metric; it is always stored and displayed.
- Some vendor sites use JavaScript rendering; if a scraper returns 0 products, the site may require a headless browser (Playwright) for reliable scraping.
