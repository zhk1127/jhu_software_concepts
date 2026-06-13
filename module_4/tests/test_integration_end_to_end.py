import pytest

from src.app import create_app


@pytest.mark.integration
def test_analysis_page_end_to_end():

    app = create_app({"TESTING": True})

    client = app.test_client()

    response = client.get("/analysis")

    assert response.status_code == 200

    html = response.data.decode()

    assert "Analysis" in html

    assert "Current database size" in html

    assert "Pull Data" in html

    assert "Update Analysis" in html

    assert html.count("Answer:") >= 11


@pytest.mark.integration
def test_update_analysis_then_reload_page():

    app = create_app({"TESTING": True})

    client = app.test_client()

    response = client.post("/update-analysis")

    assert response.status_code == 200

    response = client.get("/analysis")

    assert response.status_code == 200

    html = response.data.decode()

    assert "Analysis" in html

    assert "Answer:" in html

from src import pull_new_data


@pytest.mark.integration
def test_pull_new_data_helpers(tmp_path):
    assert pull_new_data.to_float("3.5") == 3.5
    assert pull_new_data.to_float("") is None
    assert pull_new_data.to_float("bad") is None

    assert pull_new_data.to_int("325") == 325
    assert pull_new_data.to_int("325.0") == 325
    assert pull_new_data.to_int("bad") is None

    assert pull_new_data.to_int(None) is None
    output = tmp_path / "records.json"
    pull_new_data.save_json([{"a": 1}], output)

    assert output.read_text(encoding="utf-8").strip().startswith("[")
    assert '"a": 1' in output.read_text(encoding="utf-8")


@pytest.mark.integration
def test_scrape_new_records_with_fakes(monkeypatch):
    monkeypatch.setattr(pull_new_data, "TARGET_RECORDS", 2)
    monkeypatch.setattr(pull_new_data, "get_start_page", lambda: 10)
    monkeypatch.setattr(pull_new_data.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(
        pull_new_data,
        "fetch_page_with_retries",
        lambda page: "<html>fake</html>",
    )
    monkeypatch.setattr(
        pull_new_data,
        "extract_results_from_html",
        lambda html: {"data": [{"id": 1}, {"id": 2}]},
    )
    monkeypatch.setattr(
        pull_new_data,
        "clean_record",
        lambda record: {"raw_record": {"id": record["id"]}},
    )

    records = pull_new_data.scrape_new_records()

    assert records == [
        {"raw_record": {"id": 1}},
        {"raw_record": {"id": 2}},
    ]

@pytest.mark.integration
def test_scrape_new_records_skips_none_html(monkeypatch):
    calls = {"count": 0}

    monkeypatch.setattr(pull_new_data, "TARGET_RECORDS", 1)
    monkeypatch.setattr(pull_new_data, "get_start_page", lambda: 10)
    monkeypatch.setattr(pull_new_data.time, "sleep", lambda seconds: None)

    def fake_fetch(page):
        calls["count"] += 1
        if calls["count"] == 1:
            return None
        return "<html>fake</html>"

    monkeypatch.setattr(pull_new_data, "fetch_page_with_retries", fake_fetch)
    monkeypatch.setattr(
        pull_new_data,
        "extract_results_from_html",
        lambda html: {"data": [{"id": 1}]},
    )
    monkeypatch.setattr(
        pull_new_data,
        "clean_record",
        lambda record: {"raw_record": {"id": record["id"]}},
    )

    records = pull_new_data.scrape_new_records()

    assert records == [{"raw_record": {"id": 1}}]
    assert calls["count"] == 2


@pytest.mark.integration
def test_scrape_new_records_stops_when_no_records(monkeypatch):
    monkeypatch.setattr(pull_new_data, "TARGET_RECORDS", 1)
    monkeypatch.setattr(pull_new_data, "get_start_page", lambda: 10)
    monkeypatch.setattr(
        pull_new_data,
        "fetch_page_with_retries",
        lambda page: "<html>fake</html>",
    )
    monkeypatch.setattr(
        pull_new_data,
        "extract_results_from_html",
        lambda html: {"data": []},
    )

    records = pull_new_data.scrape_new_records()

    assert records == []

@pytest.mark.integration
def test_get_start_page_returns_integer():
    start_page = pull_new_data.get_start_page()

    assert isinstance(start_page, int)
    assert start_page >= 50


@pytest.mark.integration
def test_pull_new_data_main_with_fakes(monkeypatch):
    calls = []

    fake_raw_records = [
        {"raw_record": {"id": 1}},
        {"raw_record": {"id": 2}},
    ]

    fake_cleaned_records = [
        {"raw_record": {"id": 1}, "program": "A"},
        {"raw_record": {"id": 2}, "program": "B"},
    ]

    monkeypatch.setattr(
        pull_new_data,
        "scrape_new_records",
        lambda: fake_raw_records,
    )

    def fake_save_json(data, filename):
        calls.append(("save_json", len(data), filename))

    monkeypatch.setattr(
        pull_new_data,
        "save_json",
        fake_save_json,
    )

    monkeypatch.setattr(
        pull_new_data,
        "clean_data",
        lambda records: fake_cleaned_records,
    )

    monkeypatch.setattr(
        pull_new_data,
        "insert_records_into_database",
        lambda records: (2, 0),
    )

    pull_new_data.main()

    assert ("save_json", 2, pull_new_data.RAW_OUTPUT_FILE) in calls
    assert ("save_json", 2, pull_new_data.CLEAN_OUTPUT_FILE) in calls