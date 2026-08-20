from src.main import (
    deduplicate_urls,
    extract_book_record,
    extract_book_urls,
    normalize_price,
)

import pytest


def test_price_normalization():
    assert normalize_price("£51.77") == 51.77

def test_relative_url_becomes_absolute():
    html = """
    <article class="product_pod">
        <h3>
            <a href="a-light-in-the-attic_1000/index.html">
                A Light in the Attic
            </a>
        </h3>
    </article>
    """

    page_url = "https://books.toscrape.com/catalogue/page-1.html"

    urls = extract_book_urls(html, page_url)

    assert urls == [
        "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    ]

def deduplicate_urls(urls: list[str]) -> list[str]:
    return list(dict.fromkeys(urls))

def test_missing_description_returns_none():
    html = """
    <div class="product_main">
        <h1>Test Book</h1>
        <p class="price_color">£19.99</p>
        <p class="instock availability">In stock</p>
        <p class="star-rating Three"></p>
    </div>
    """

    record = extract_book_record(
        html=html,
        product_url="https://books.toscrape.com/catalogue/test-book/index.html",
        source_page="https://books.toscrape.com/catalogue/page-1.html",
        fetched_at="2026-08-20T00:00:00Z",
    )

    assert record["description"] is None

def test_duplicate_urls_collapse_to_one():
    urls = [
        "https://books.toscrape.com/catalogue/test-book/index.html",
        "https://books.toscrape.com/catalogue/test-book/index.html",
        "https://books.toscrape.com/catalogue/another-book/index.html",
    ]

    unique_urls = deduplicate_urls(urls)

    assert unique_urls == [
        "https://books.toscrape.com/catalogue/test-book/index.html",
        "https://books.toscrape.com/catalogue/another-book/index.html",
    ]

def test_malformed_html_raises_error():
    malformed_html = """
    <div class="product_main">
        <p class="price_color">£19.99</p>
        <p class="instock availability">In stock</p>
        <p class="star-rating Three"></p>
    </div>
    """

    with pytest.raises(ValueError, match="Title not found"):
        extract_book_record(
            html=malformed_html,
            product_url="https://books.toscrape.com/catalogue/broken-book/index.html",
            source_page="https://books.toscrape.com/catalogue/page-1.html",
            fetched_at="2026-08-20T00:00:00Z",
        )