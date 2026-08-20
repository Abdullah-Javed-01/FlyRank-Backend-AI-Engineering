from pathlib import Path
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime, timezone
from pydantic import BaseModel, ValidationError, field_validator

CATALOGUE_URL = "https://books.toscrape.com/catalogue/page-1.html"

CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"

USER_AGENT = (
    "FlyRankInternship-BE05/1.0 "
    "(+https://github.com/Abdullah-Javed-01/FlyRank-Backend-AI-Engineering)"
)

TIMEOUT_SECONDS = 10
REQUEST_DELAY_SECONDS = 0.5
OUTPUT_DIR = Path("output")

class BookRecord(BaseModel):
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: str | None
    source_page: str
    fetched_at: str

    @field_validator("product_url", "source_page")
    @classmethod
    def require_https(cls, value: str) -> str:
        if not value.startswith("https://"):
            raise ValueError("URL must start with https://")
        return value

def fetch_or_cache(url: str, cache_path: Path) -> str:
    if cache_path.exists():
        cached_content = cache_path.read_bytes()

        print(
            f"CACHE HIT "
            f"path={cache_path} "
            f"bytes={len(cached_content)}"
        )

        return cached_content.decode("utf-8", errors="replace")

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    time.sleep(REQUEST_DELAY_SECONDS)
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT_SECONDS,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch {url}: HTTP {response.status_code}"
        )

    content = response.content

    cache_path.write_bytes(content)

    print(
        f"FETCH "
        f"status={response.status_code} "
        f"bytes={len(content)}"
    )

    return content.decode("utf-8", errors="replace")

def extract_book_urls(html: str, page_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")

    book_urls = []

    for link in soup.select("article.product_pod h3 a[href]"):
        absolute_url = urljoin(page_url, link["href"])
        book_urls.append(absolute_url)

    return book_urls

def extract_next_page_url(html: str, page_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")

    next_link = soup.select_one("li.next a[href]")

    if next_link is None:
        return None

    return urljoin(page_url, next_link["href"])

def get_fetched_at(cache_path: Path) -> str:
    timestamp = cache_path.stat().st_mtime

    return (
        datetime.fromtimestamp(timestamp, tz=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )

def extract_book_record(
    html: str,
    product_url: str,
    source_page: str,
    fetched_at: str,
) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    product = soup.select_one("div.product_main")

    if product is None:
        raise ValueError(f"Product section not found: {product_url}")

    title_element = product.select_one("h1")
    price_element = product.select_one("p.price_color")
    availability_element = product.select_one("p.instock.availability")
    rating_element = product.select_one("p.star-rating")

    if title_element is None:
        raise ValueError(f"Title not found: {product_url}")

    if price_element is None:
        raise ValueError(f"Price not found: {product_url}")

    if availability_element is None:
        raise ValueError(f"Availability not found: {product_url}")

    if rating_element is None:
        raise ValueError(f"Rating not found: {product_url}")

    rating_classes = rating_element.get("class", [])
    rating_text = next(
        (
            class_name
            for class_name in rating_classes
            if class_name != "star-rating"
        ),
        None,
    )

    description = None

    description_heading = soup.select_one("#product_description")

    if description_heading is not None:
        description_element = description_heading.find_next_sibling("p")

        if description_element is not None:
            description = description_element.get_text(
                " ",
                strip=True,
            )

    return {
        "title": title_element.get_text(strip=True),
        "product_url": product_url,
        "price_text": price_element.get_text(strip=True),
        "availability_text": availability_element.get_text(
            " ",
            strip=True,
        ),
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at,
    }
    
def normalize_price(price_text: str) -> float:
    cleaned = price_text.strip()

    if not cleaned.startswith("£"):
        raise ValueError(f"Unexpected price format: {price_text}")

    return float(cleaned.removeprefix("£"))

def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

def main():
    current_url = CATALOGUE_URL
    catalogue_pages = 0
    discovered = 0

    book_sources: dict[str, str] = {}

    while current_url is not None and catalogue_pages < 3:
        catalogue_pages += 1

        cache_path = CACHE_DIR / f"catalogue-page-{catalogue_pages}.html"

        html = fetch_or_cache(current_url, cache_path)

        page_book_urls = extract_book_urls(html, current_url)

        discovered += len(page_book_urls)

        for book_url in page_book_urls:
            book_sources.setdefault(book_url, current_url)

        current_url = extract_next_page_url(html, current_url)

    raw_records = []

    for index, (product_url, source_page) in enumerate(
        book_sources.items(),
        start=1,
    ):
        book_cache_path = CACHE_DIR / f"book-{index:03d}.html"

        book_html = fetch_or_cache(
            product_url,
            book_cache_path,
        )

        fetched_at = get_fetched_at(book_cache_path)

        record = extract_book_record(
            book_html,
            product_url,
            source_page,
            fetched_at,
        )

        raw_records.append(record)
        
    valid_records_by_url: dict[str, dict] = {}
    errors = []

    for raw_record in raw_records:
        try:
            candidate = {
                **raw_record,
                "price_gbp": normalize_price(
                    raw_record["price_text"]
                ),
            }

            validated = BookRecord.model_validate(candidate)
            clean_record = validated.model_dump()

            valid_records_by_url[
                validated.product_url
            ] = clean_record

        except (ValidationError, ValueError) as exc:
            errors.append(
                {
                    "product_url": raw_record.get("product_url"),
                    "reason": str(exc),
                }
            )

    valid_records = list(valid_records_by_url.values())

    write_json(
        OUTPUT_DIR / "books.json",
        valid_records,
    )

    write_json(
        OUTPUT_DIR / "errors.json",
        errors,
    )

    print(
        json.dumps(
            valid_records[0],
            indent=2,
            ensure_ascii=False,
        )
    )

    print(f"valid_records={len(valid_records)}")
    print(f"invalid_records={len(errors)}")
    print(f"detail_pages={len(raw_records)}")
    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={discovered}")
    print(f"unique_urls={len(book_sources)}")


if __name__ == "__main__":
    main()