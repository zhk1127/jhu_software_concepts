"""
Flask web application for GradCafe analytics.

This module creates the Flask application, renders the analytics
dashboard, launches background data pulls, and refreshes SQL
analysis results stored in PostgreSQL.
"""

import sys

from flask import Flask, jsonify, redirect, render_template, url_for
from publisher import publish_task
from src.load_data import get_database_count
from src.query_data import get_analysis_results


def create_app(config=None):
    """
    Create and configure the Flask application.

    Args:
        config (dict, optional):
            Optional configuration overrides used during testing.

    Returns:
        Flask:
            Configured Flask application instance.
    """
    flask_app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    flask_app.config.update(
        TESTING=False,
        PULL_PROCESS=None,
        CACHED_RESULTS=None,
        SCRAPER_COMMAND=[sys.executable, "-m", "src.pull_new_data"],
    )

    if config:
        flask_app.config.update(config)

    def pull_running():
        """Return whether a background data pull is currently running."""
        process = flask_app.config.get("PULL_PROCESS")

        if process is None:
            return False

        if process.poll() is None:
            return True

        flask_app.config["PULL_PROCESS"] = None
        return False

    def get_cached_results():
        """Return cached analysis results, computing them if needed."""
        if flask_app.config.get("CACHED_RESULTS") is None:
            flask_app.config["CACHED_RESULTS"] = get_analysis_results()

        return flask_app.config["CACHED_RESULTS"]

    @flask_app.route("/")
    def home():
        """Redirect the home page to the analysis dashboard."""
        return redirect(url_for("analysis"))

    @flask_app.route("/analysis")
    def analysis():
        """Render the GradCafe analysis dashboard."""
        is_running = pull_running()

        if is_running:
            pull_status = (
                "Pull Data is currently running. The app is scraping approximately "
                "500 additional GradCafe records and inserting new records into PostgreSQL."
            )
        else:
            pull_status = (
                "No data pull is currently running. New data has been added if available. "
                "Click Update Analysis to refresh the SQL results."
            )

        return render_template(
            "index.html",
            results=get_cached_results(),
            database_count=get_database_count(),
            pull_running=is_running,
            pull_status=pull_status,
            message="",
        )

    @flask_app.route("/pull-data", methods=["POST"])
    def pull_data():
        """Queue a background data pull task."""
        try:
            publish_task("scrape_new_data", payload={})
            return jsonify({"status": "queued", "task": "scrape_new_data"}), 202
        except RuntimeError:
            flask_app.logger.exception("Failed to publish scrape_new_data")
            return jsonify({"error": "publish_failed"}), 503

    @flask_app.route("/update-analysis", methods=["POST"])
    def update_analysis():
        """Queue an analytics recompute task."""
        try:
            publish_task("recompute_analytics", payload={})
            return jsonify({"status": "queued", "task": "recompute_analytics"}), 202
        except RuntimeError:
            flask_app.logger.exception("Failed to publish recompute_analytics")
            return jsonify({"error": "publish_failed"}), 503

    return flask_app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=5000, debug=True)
