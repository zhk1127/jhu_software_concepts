"""Tests for GradCafe scraping helper functions."""

import html
import json

from src.worker.etl import scrape


def test_build_url():
    """build_url includes the page number and newest sort order."""
    url = scrape.build_url(5)

    assert "page=5" in url
    assert "sort=newest" in url


def test_clean_record():
    """clean_record maps GradCafe result fields into normalized fields."""
    record = {
        "id": 1,
        "program": "CS",
        "school": "MIT",
        "notes": "hello",
        "added_on_label": "Jan 01, 2026",
        "decision": "Accepted",
        "season": "Fall 2026",
        "status": "International",
        "greq": "165",
        "grev": "160",
        "level": "PhD",
        "ugpa": "3.9",
        "grew": "4.5",
    }

    result = scrape.clean_record(record)

    assert result["program"] == "CS"
    assert result["university"] == "MIT"
    assert result["url"].endswith("/1")
    assert result["US/International"] == "International"


def test_save_load(tmp_path):
    """save_data and load_data round-trip JSON records."""
    file_path = tmp_path / "records.json"

    scrape.save_data([{"x": 1}], file_path)

    assert scrape.load_data(file_path) == [{"x": 1}]


def test_load_missing():
    """load_data returns an empty list when the file is missing."""
    assert scrape.load_data("missing_file.json") == []


def test_deduplicate():
    """_deduplicate_by_url removes later duplicate URLs."""
    records = [{"url": "a"}, {"url": "a"}, {"url": "b"}]

    result = scrape._deduplicate_by_url(records)

    assert result == [{"url": "a"}, {"url": "b"}]


def test_extract_results():
    """extract_results_from_html parses embedded GradCafe JSON state."""
    payload = {
        "props": {
            "results": {
                "data": [],
                "meta": {"last_page": 1},
            }
        }
    }
    encoded = html.escape(json.dumps(payload), quote=True)
    html_text = f'<div id="app" data-page="{encoded}"></div>'

    result = scrape.extract_results_from_html(html_text)

    assert result["meta"]["last_page"] == 1


def test_extract_results_missing_app_div():
    """extract_results_from_html raises when app div is missing."""
    try:
        scrape.extract_results_from_html("<html></html>")
    except ValueError as exc:
        assert "id='app'" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_extract_results_missing_data_page():
    """extract_results_from_html raises when data-page is missing."""
    try:
        scrape.extract_results_from_html('<div id="app"></div>')
    except ValueError as exc:
        assert "data-page" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_fetch_page_success(monkeypatch):
    """fetch_page decodes successful HTTP responses."""
    class Response:
        """Fake urllib3 response."""

        status = 200
        data = b"hello"

    class FakeHttp:
        """Fake urllib3 pool manager."""

        def request(self, method, url, headers):
            assert method == "GET"
            assert "page=2" in url
            assert "User-Agent" in headers
            return Response()

    monkeypatch.setattr(scrape, "http", FakeHttp())

    assert scrape.fetch_page(2) == "hello"


def test_fetch_page_failure(monkeypatch):
    """fetch_page raises RuntimeError for non-200 responses."""
    class Response:
        """Fake urllib3 response."""

        status = 500
        data = b""

    class FakeHttp:
        """Fake urllib3 pool manager."""

        def request(self, method, url, headers):
            return Response()

    monkeypatch.setattr(scrape, "http", FakeHttp())

    try:
        scrape.fetch_page(2)
    except RuntimeError as exc:
        assert "Request failed" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")


def test_fetch_page_with_retries_success(monkeypatch):
    """fetch_page_with_retries returns content after a transient failure."""
    calls = {"count": 0}

    def fake_fetch(page):
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("temporary")
        return f"page-{page}"

    monkeypatch.setattr(scrape, "fetch_page", fake_fetch)
    monkeypatch.setattr(scrape.time, "sleep", lambda seconds: None)

    assert scrape.fetch_page_with_retries(3) == "page-3"


def test_fetch_page_with_retries_failure(monkeypatch):
    """fetch_page_with_retries returns None after max retries."""
    def fake_fetch(page):
        raise RuntimeError(f"bad {page}")

    monkeypatch.setattr(scrape, "fetch_page", fake_fetch)
    monkeypatch.setattr(scrape.time, "sleep", lambda seconds: None)

    assert scrape.fetch_page_with_retries(3) is None


def test_scrape_data(monkeypatch, tmp_path):
    """scrape_data fetches, cleans, deduplicates, and saves records."""
    page_one = {
        "data": [
            {
                "id": 1,
                "program": "CS",
                "school": "MIT",
            }
        ],
        "meta": {"last_page": 1},
    }

    monkeypatch.setattr(scrape, "load_data", lambda filename=scrape.OUTPUT_FILE: [])
    monkeypatch.setattr(scrape, "fetch_page_with_retries", lambda page: "html")
    monkeypatch.setattr(scrape, "extract_results_from_html", lambda html_text: page_one)
    monkeypatch.setattr(scrape, "save_data", lambda data, filename=scrape.OUTPUT_FILE: None)
    monkeypatch.setattr(scrape.time, "sleep", lambda seconds: None)

    result = scrape.scrape_data(target_records=1)

    assert len(result) == 1
    assert result[0]["url"].endswith("/1")


def test_scrape_data_skips_failed_page_then_stops(monkeypatch):
    """scrape_data handles a failed page and then stops on empty data."""
    calls = {"count": 0}

    def fake_fetch(page):
        calls["count"] += 1
        if calls["count"] == 1:
            return None
        return "html"

    def fake_extract(html_text):
        return {"data": [], "meta": {"last_page": 2}}

    monkeypatch.setattr(scrape, "load_data", lambda filename=scrape.OUTPUT_FILE: [])
    monkeypatch.setattr(scrape, "fetch_page_with_retries", fake_fetch)
    monkeypatch.setattr(scrape, "extract_results_from_html", fake_extract)
    monkeypatch.setattr(scrape, "save_data", lambda data, filename=scrape.OUTPUT_FILE: None)
    monkeypatch.setattr(scrape.time, "sleep", lambda seconds: None)

    assert scrape.scrape_data(target_records=1) == []


def test_scrape_data_truncates_to_target(monkeypatch):
    """scrape_data truncates collected records to target size."""
    page_data = {
        "data": [
            {"id": 1, "program": "A", "school": "S"},
            {"id": 2, "program": "B", "school": "S"},
        ],
        "meta": {"last_page": 10},
    }

    monkeypatch.setattr(scrape, "load_data", lambda filename=scrape.OUTPUT_FILE: [])
    monkeypatch.setattr(scrape, "fetch_page_with_retries", lambda page: "html")
    monkeypatch.setattr(scrape, "extract_results_from_html", lambda html_text: page_data)
    monkeypatch.setattr(scrape, "save_data", lambda data, filename=scrape.OUTPUT_FILE: None)
    monkeypatch.setattr(scrape.time, "sleep", lambda seconds: None)

    result = scrape.scrape_data(target_records=1)

    assert len(result) == 1
