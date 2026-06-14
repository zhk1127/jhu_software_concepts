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

@pytest.mark.web
def test_home_redirects_to_analysis():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 302
    assert "/analysis" in response.headers["Location"]


class FinishedProcess:
    def poll(self):
        return 0


class RunningProcess:
    def poll(self):
        return None


@pytest.mark.web
def test_analysis_clears_finished_process():
    app = create_app(
        {
            "TESTING": True,
            "PULL_PROCESS": FinishedProcess(),
        }
    )
    client = app.test_client()

    response = client.get("/analysis")

    assert response.status_code == 200
    assert app.config["PULL_PROCESS"] is None


@pytest.mark.web
def test_analysis_shows_running_status():
    app = create_app(
        {
            "TESTING": True,
            "PULL_PROCESS": RunningProcess(),
        }
    )
    client = app.test_client()

    response = client.get("/analysis")
    html = response.data.decode()

    assert response.status_code == 200
    assert "Pull Data is currently running" in html

    import runpy
from src import app as app_module

