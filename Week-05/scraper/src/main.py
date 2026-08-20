from pathlib import Path

import requests


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

def main():
    html = fetch_or_cache(CATALOGUE_URL, CACHE_FILE)


if __name__ == "__main__":
    main()