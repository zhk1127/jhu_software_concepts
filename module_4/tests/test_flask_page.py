import pytest

from src.app import create_app


@pytest.mark.web
def test_analysis_page_loads():

    app = create_app({"TESTING": True})

    client = app.test_client()

    response = client.get("/analysis")

    assert response.status_code == 200

    html = response.data.decode()

    assert "Analysis" in html

    assert "Pull Data" in html

    assert "Update Analysis" in html

    assert "Answer:" in html