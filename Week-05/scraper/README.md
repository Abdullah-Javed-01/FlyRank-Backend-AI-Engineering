# The Polite Scraper

FlyRank Backend AI Engineering — Week 5 — BE-05

A polite web scraping pipeline built in Python for the Books to Scrape practice sandbox.

## Target Classification

### Target

This scraper targets:

https://books.toscrape.com/

Books to Scrape is part of ToScrape, which describes it as a fictional bookstore that is intentionally provided for practicing web scraping. The ToScrape website states that it is a safe place for beginners learning web scraping and for developers validating scraping technologies.

### Scope

This project will process only the first 3 catalogue pages of Books to Scrape.

The expected scope is:

- 3 catalogue pages
- 20 books per catalogue page
- 60 books in total
- 60 book detail pages

The scraper will not crawl the complete website.

### Data Collected

For each book, the scraper will collect:

- title
- product URL
- price text
- availability text
- rating text
- description
- source catalogue page
- fetch timestamp

Later stages will normalize and validate this data before it is stored.

### robots.txt Check

I checked:

https://books.toscrape.com/robots.txt

The server returned HTTP 404 Not Found.

**Result: no robots file found.**

A missing robots.txt file is not treated as permission. The scraping target is appropriate because Books to Scrape is explicitly provided by ToScrape as a practice environment for web scraping.

### Responsible Use

I will not reuse this code on another site without checking its rules and terms first.