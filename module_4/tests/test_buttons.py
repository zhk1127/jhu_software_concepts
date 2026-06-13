import pytest

from src.app import create_app


class FakeProcess:
    def poll(self):
        return 0


class FakeBusyProcess:
    def poll(self):
        return None


@pytest.mark.buttons
def test_pull_data_endpoint_starts_process(monkeypatch):
    calls = []

    def fake_popen(command):
        calls.append(command)
        return FakeProcess()

    monkeypatch.setattr("src.app.subprocess.Popen", fake_popen)

    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.post("/pull-data")

    assert response.status_code == 200
    assert response.get_json() == {"ok": True}
    assert len(calls) == 1


@pytest.mark.buttons
def test_update_analysis_endpoint_returns_ok():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.post("/update-analysis")

    assert response.status_code == 200
    assert response.get_json() == {"ok": True}


@pytest.mark.buttons
def test_pull_data_returns_busy_when_process_running():
    app = create_app(
        {
            "TESTING": True,
            "PULL_PROCESS": FakeBusyProcess(),
        }
    )
    client = app.test_client()

    response = client.post("/pull-data")

    assert response.status_code == 409
    assert response.get_json() == {"busy": True}


@pytest.mark.buttons
def test_update_analysis_returns_busy_when_process_running():
    app = create_app(
        {
            "TESTING": True,
            "PULL_PROCESS": FakeBusyProcess(),
        }
    )
    client = app.test_client()

    response = client.post("/update-analysis")

    assert response.status_code == 409
    assert response.get_json() == {"busy": True}