from pathlib import Path
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

REQUEST_DELAY_SECONDS = 0.5
CATALOGUE_URL = "https://books.toscrape.com/catalogue/page-1.html"

CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"

USER_AGENT = (
    "FlyRankInternship-BE05/1.0 "
    "(+https://github.com/Abdullah-Javed-01/FlyRank-Backend-AI-Engineering)"
)

TIMEOUT_SECONDS = 10

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

    cache_path.write_bytes(response.content)

    print(
        f"FETCH "
        f"status={response.status_code} "
        f"bytes={len(response.content)}"
    )

    return response.text

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

    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={discovered}")
    print(f"unique_urls={len(book_sources)}")


if __name__ == "__main__":
    main()