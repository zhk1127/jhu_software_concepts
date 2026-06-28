"""Tests for Flask page rendering."""

import pytest

from src.web.app.app import create_app


@pytest.mark.web
def test_home_redirects_to_analysis():
    """The home page redirects to the analysis dashboard."""
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 302
    assert "/analysis" in response.location


@pytest.mark.web
def test_analysis_page_loads():
    """The analysis page loads and shows the dashboard."""
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.get("/analysis")
    html = response.data.decode()

    assert response.status_code == 200
    assert "Grad School Cafe Data Analysis" in html
    assert "Pull Data" in html
    assert "Update Analysis" in html


@pytest.mark.web
def test_analysis_shows_async_queue_status():
    """The analysis page explains that tasks are queued through RabbitMQ."""
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.get("/analysis")
    html = response.data.decode()

    assert response.status_code == 200
    assert "RabbitMQ" in html
    assert "processed asynchronously" in html


@pytest.mark.web
def test_analysis_includes_database_count():
    """The analysis page displays the current database size."""
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.get("/analysis")
    html = response.data.decode()

    assert response.status_code == 200
    assert "Current database size" in html
