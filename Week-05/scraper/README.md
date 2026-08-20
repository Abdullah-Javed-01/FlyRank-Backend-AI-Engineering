# The Polite Scraper

FlyRank Backend AI Engineering — Week 5 — Assignment A9 / BE-05

A polite Python scraping pipeline that processes the first three catalogue pages of the Books to Scrape practice sandbox, discovers 60 unique book URLs, extracts and validates 60 book records, caches responses, survives a deliberately broken page, and produces an honest run report.

---

## Target Classification

### Target

This scraper targets:

https://books.toscrape.com/

Books to Scrape is part of ToScrape and is intentionally provided as a practice sandbox for learning and testing web scraping.

### Scope

The scraper processes only the first **3 catalogue pages**.

Expected scope:

- 3 catalogue pages
- 20 books per catalogue page
- 60 discovered books
- 60 valid book detail records

The scraper does not crawl the complete website.

### Data Collected

For every book, the raw extraction contains these eight fields:

- `title`
- `product_url`
- `price_text`
- `availability_text`
- `rating_text`
- `description`
- `source_page`
- `fetched_at`

During normalization, `price_gbp` is added as a numeric value while the original `price_text` is preserved.

### robots.txt Check

Checked:

https://books.toscrape.com/robots.txt

The server returned:

```text
404 Not Found
```

**Result: no robots file found.**

A missing `robots.txt` file is not treated as permission. This target is appropriate because Books to Scrape is explicitly provided as a practice environment for web scraping.

**I will not reuse this code on another site without checking its rules and terms first.**

---

## Python Lane

This project uses the Python lane:

- Python 3.10+
- Requests
- Beautiful Soup
- Pydantic
- Python standard-library `json`
- pytest for parser tests

The project was developed and tested with Python 3.12.

Playwright and `psutil` are used only for the required browser-cost comparison and are intentionally kept separate from the core scraper dependencies.

---

## Project Structure

```text
scraper/
├── src/
│   └── main.py
├── tests/
│   └── test_parser.py
├── output/
│   ├── books.json
│   ├── errors.json
│   ├── run-report.json
│   └── browser-cost.json
├── cache/                     # generated locally and ignored by Git
├── benchmark_browser.py
├── requirements.txt
├── requirements-benchmark.txt
├── .gitignore
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Abdullah-Javed-01/FlyRank-Backend-AI-Engineering.git
cd FlyRank-Backend-AI-Engineering/Week-05/scraper
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Install the core scraper and test dependencies:

```bash
pip install -r requirements.txt
```

---

## Run the Scraper

The documented run command is:

```bash
python src/main.py
```

A clean run processes exactly the first three catalogue pages, follows the catalogue's own next-page links, discovers 60 unique books, visits the corresponding detail pages, validates the records, and writes the outputs.

Generated files:

```text
output/books.json
output/errors.json
output/run-report.json
```

The cache is reused on later runs, so development does not repeatedly request the same pages from the site.

---

## Expected Result

A successful run produces:

```text
valid_records=60
invalid_records=0
detail_pages=60
catalogue_pages=3
discovered=60
unique_urls=60
attempted_detail_urls=61
failed_pages=1
```

The extra attempted detail URL is the deliberately broken URL used to prove that one failed page does not crash the full job.

A rerun still produces exactly **60 valid unique records**, not 120.

---

## Record Schema

Each validated record has the following shape:

| Field | Type | Required | Purpose |
|---|---|---:|---|
| `title` | string | Yes | Book title |
| `product_url` | string | Yes | Canonical HTTPS identity for the book |
| `price_text` | string | Yes | Original scraped price text |
| `price_gbp` | number | Yes | Normalized numeric GBP price |
| `availability_text` | string | Yes | Scraped availability text |
| `rating_text` | string | Yes | Scraped star-rating label |
| `description` | string or null | Yes | Description when present; `null` when missing |
| `source_page` | string | Yes | Catalogue page where the book was discovered |
| `fetched_at` | string | Yes | UTC fetch/cache timestamp used as provenance |

Pydantic validates each normalized record before it is stored.

Records that fail validation are written to:

```text
output/errors.json
```

with the reason for failure.

---

## Politeness Rules

Every real request follows the same rules.

### Identifying User-Agent

```text
FlyRankInternship-BE05/1.0 (+https://github.com/Abdullah-Javed-01/FlyRank-Backend-AI-Engineering)
```

### Delay

The scraper waits at least:

```text
0.5 seconds
```

before each real request.

Cached reads do not wait because they do not contact the website.

### Timeout

Every real request has a:

```text
10 second
```

timeout.

### Status Handling

Only HTTP `200` responses are parsed as HTML.

Timeouts and `5xx` server failures are retried once after a short wait.

HTTP `403` and `404` responses are not retried.

### Cache

Downloaded HTML is stored under:

```text
cache/
```

Development reruns read from the cache instead of repeatedly contacting the practice site.

The cache directory is excluded from Git.

---

## URL Normalization and Idempotency

Relative links are converted into absolute URLs using Python's `urljoin()` rather than string concatenation.

Duplicate URLs are removed before detail processing.

The canonical `product_url` is also used as the stable identity of each validated record.

Because `output/books.json` is rewritten from the validated unique records on each run, rerunning the scraper does not append duplicates.

---

## Failure Handling

The scraper deliberately adds this nonexistent book URL during the Stage 5 failure test:

```text
https://books.toscrape.com/catalogue/flyrank-intentional-missing-book/index.html
```

That request returns HTTP `404`.

The failed page is logged and skipped while the 60 valid records survive.

Verified result:

```text
valid_records=60
invalid_records=0
failed_pages=1
```

---

## Parser Tests

The assignment requires at least five parser unit tests.

Run them with:

```bash
python -m pytest -v
```

Implemented cases:

1. price normalization
2. relative URL to absolute URL conversion
3. missing description returns `None`
4. duplicate URLs collapse to unique URLs
5. malformed HTML raises a parser error

Verified result:

```text
5 passed in 0.91s
```

---

## Real Run Report

The following is a real cached rerun from the completed scraper:

```json
{
  "started_at": "2026-08-20T14:12:35.869649Z",
  "duration_seconds": 4.047,
  "catalogue_pages": 3,
  "discovered_urls": 60,
  "unique_urls": 60,
  "attempted_detail_urls": 61,
  "pages_fetched": 0,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1,
  "failed_page_details": [
    {
      "url": "https://books.toscrape.com/catalogue/flyrank-intentional-missing-book/index.html",
      "reason": "HTTP 404: https://books.toscrape.com/catalogue/flyrank-intentional-missing-book/index.html"
    }
  ]
}
```

This report is from a rerun, so `pages_fetched` is `0` and `cache_hits` is `63`. That demonstrates that the catalogue and valid detail pages were served from the local cache while the deliberately broken URL was still handled as a failed page.

---

## Browser-Cost Comparison

The assignment also requires comparing plain HTTP with a real browser on:

https://quotes.toscrape.com/js/

The comparison is implemented in:

```text
benchmark_browser.py
```

Install the benchmark-only dependencies:

```bash
pip install -r requirements-benchmark.txt
python -m playwright install chromium
```

Run:

```bash
python benchmark_browser.py
```

Measured on the development machine:

| Method | Elapsed Time | Observed Process-Tree Memory | Quotes Found |
|---|---:|---:|---:|
| Plain HTTP | 1.284 s | 43.89 MB | 0 |
| Playwright | 7.183 s | 384.64 MB | 10 |

The memory values are observed process-tree RSS snapshots from the benchmark, not continuously sampled true peak-memory measurements.

Plain HTTP returned HTTP `200`, but the quote elements were not present in the server HTML because that page renders them with JavaScript. Playwright executed the page JavaScript and found 10 quotes.

**The core Books to Scrape assignment needed no browser because its book data is already present in the HTML the server sends, so using a browser would only add time and memory cost.**

The raw benchmark evidence is stored in:

```text
output/browser-cost.json
```

---

## Honest Limitation

The parser depends on the current HTML structure and CSS selectors used by Books to Scrape. If that practice site's markup changes significantly, the selectors may need to be updated before the scraper can extract the same fields correctly.

The scraper is also intentionally limited to the first three catalogue pages rather than the entire site.

---

## Ethics

When an official API exists, I would prefer it over scraping. I would not bypass authentication, paywalls, access blocks, or other restrictions. I would collect only the data needed for the task, identify automated requests honestly, and avoid placing unnecessary load on a site.

---

## Development History

The assignment was built incrementally with one meaningful commit per required stage:

```text
Stage 0: classify scraping target
Stage 1: fetch and cache HTML
Stage 2: discover three catalogue pages
Stage 3: extract book details
Stage 4: validate normalized records
Stage 5: survive failures, report the run
Stage 6: publish scraper evidence
```

---

## Author

**Abdullah Javed**

Backend AI Engineering Intern — FlyRank AI

- GitHub: [Abdullah-Javed-01](https://github.com/Abdullah-Javed-01)
- LinkedIn: [Abdullah Javed](https://www.linkedin.com/in/abdullah-javed-id01/)
