import re

import pytest

from src.app import create_app


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