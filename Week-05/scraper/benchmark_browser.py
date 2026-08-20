import json
import time
from pathlib import Path

import psutil
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


TARGET_URL = "https://quotes.toscrape.com/js/"
OUTPUT_FILE = Path("output/browser-cost.json")


def process_tree_memory_mb() -> float:
    process = psutil.Process()
    processes = [process]

    try:
        processes.extend(process.children(recursive=True))
    except psutil.Error:
        pass

    total_bytes = 0

    for proc in processes:
        try:
            total_bytes += proc.memory_info().rss
        except psutil.Error:
            continue

    return total_bytes / (1024 * 1024)


def benchmark_http() -> dict:
    start_memory = process_tree_memory_mb()
    start_time = time.perf_counter()

    response = requests.get(TARGET_URL, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    quote_count = len(soup.select(".quote"))

    elapsed = time.perf_counter() - start_time
    end_memory = process_tree_memory_mb()

    return {
        "method": "plain_http",
        "elapsed_seconds": round(elapsed, 3),
        "memory_mb": round(max(start_memory, end_memory), 2),
        "quotes_found": quote_count,
        "status_code": response.status_code,
    }


def benchmark_playwright() -> dict:
    start_memory = process_tree_memory_mb()
    start_time = time.perf_counter()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(
            TARGET_URL,
            wait_until="networkidle",
            timeout=30000,
        )

        quote_count = page.locator(".quote").count()
        browser_memory = process_tree_memory_mb()

        browser.close()

    elapsed = time.perf_counter() - start_time

    return {
        "method": "playwright",
        "elapsed_seconds": round(elapsed, 3),
        "memory_mb": round(max(start_memory, browser_memory), 2),
        "quotes_found": quote_count,
        "status_code": 200,
    }


def main():
    results = {
        "target": TARGET_URL,
        "plain_http": benchmark_http(),
        "playwright": benchmark_playwright(),
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()