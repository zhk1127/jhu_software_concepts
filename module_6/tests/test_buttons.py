"""Tests for Flask button endpoints."""

import pytest

from src.web.app.app import create_app


@pytest.mark.buttons
def test_pull_data_endpoint_queues_task(monkeypatch):
    """Pull Data should enqueue a scrape task."""

    calls = []

    def fake_publish_task(kind, payload=None, headers=None):
        calls.append((kind, payload, headers))

    monkeypatch.setattr("src.web.app.app.publish_task", fake_publish_task)

    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.post("/pull-data")

    assert response.status_code == 202
    assert response.get_json() == {
        "status": "queued",
        "task": "scrape_new_data",
    }
    assert calls == [("scrape_new_data", {}, None)]


@pytest.mark.buttons
def test_update_analysis_endpoint_queues_task(monkeypatch):
    """Update Analysis should enqueue a recompute task."""

    calls = []

    def fake_publish_task(kind, payload=None, headers=None):
        calls.append((kind, payload, headers))

    monkeypatch.setattr("src.web.app.app.publish_task", fake_publish_task)

    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.post("/update-analysis")

    assert response.status_code == 202
    assert response.get_json() == {
        "status": "queued",
        "task": "recompute_analytics",
    }
    assert calls == [("recompute_analytics", {}, None)]


@pytest.mark.buttons
def test_pull_data_returns_503_when_publish_fails(monkeypatch):
    """Pull Data should return 503 when publishing fails."""

    def fake_publish_task(kind, payload=None, headers=None):
        raise RuntimeError("RabbitMQ unavailable")

    monkeypatch.setattr("src.web.app.app.publish_task", fake_publish_task)

    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.post("/pull-data")

    assert response.status_code == 503
    assert response.get_json() == {"error": "publish_failed"}


@pytest.mark.buttons
def test_update_analysis_returns_503_when_publish_fails(monkeypatch):
    """Update Analysis should return 503 when publishing fails."""

    def fake_publish_task(kind, payload=None, headers=None):
        raise RuntimeError("RabbitMQ unavailable")

    monkeypatch.setattr("src.web.app.app.publish_task", fake_publish_task)

    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.post("/update-analysis")

    assert response.status_code == 503
    assert response.get_json() == {"error": "publish_failed"}