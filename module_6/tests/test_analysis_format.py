import re

import pytest

from src.web.app.app import create_app


@pytest.mark.analysis
def test_analysis_page_contains_answer_labels():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.get("/analysis")
    html = response.data.decode()

    assert response.status_code == 200
    assert html.count("Answer:") >= 11


@pytest.mark.analysis
def test_percentages_are_rendered_with_two_decimals():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.get("/analysis")
    html = response.data.decode()

    percentages = re.findall(r"\d+\.\d+%", html)

    assert response.status_code == 200
    assert len(percentages) >= 1

    for percentage in percentages:
        assert re.match(r"^\d+\.\d{2}%$", percentage)

from src.worker.etl import query_data


@pytest.mark.analysis
def test_get_llm_q9_count(monkeypatch):

    class FakeCursor:
        def execute(self, *args, **kwargs):
            pass

        def fetchone(self):
            return (1,)

        def close(self):
            pass

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def close(self):
            pass

    monkeypatch.setattr(
        query_data.psycopg,
        "connect",
        lambda **kwargs: FakeConnection(),
    )

    assert query_data.get_llm_q9_count() == 1

import runpy
from src.worker.etl import query_data

@pytest.mark.analysis
def test_query_data_main(monkeypatch):

    monkeypatch.setattr(
        query_data,
        "get_analysis_results",
        lambda: {"Q1": "answer"}
    )

    runpy.run_module(
        "src.worker.etl.query_data",
        run_name="__main__"
    )