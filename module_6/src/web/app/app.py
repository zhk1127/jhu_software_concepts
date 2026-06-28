"""Flask web application for GradCafe analytics."""

from flask import Flask, jsonify, redirect, render_template, url_for

from src.db.load_data import get_database_count
from src.web.publisher import publish_task
from src.worker.etl.query_data import get_analysis_results


def create_app(config=None):
    """Create and configure the Flask application."""
    flask_app = Flask(
        __name__,
        template_folder="../../../templates",
        static_folder="../../../static",
    )

    flask_app.config.update(
        TESTING=False,
        CACHED_RESULTS=None,
    )

    if config:
        flask_app.config.update(config)

    @flask_app.route("/")
    def home():
        """Redirect the home page to the analysis dashboard."""
        return redirect(url_for("analysis"))

    @flask_app.route("/analysis")
    def analysis():
        """Render the GradCafe analysis dashboard."""
        pull_status = (
            "No data pull is currently running in the web process. "
            "Pull Data and Update Analysis requests are queued through RabbitMQ "
            "and processed asynchronously by the worker service."
        )

        return render_template(
            "index.html",
            results=get_analysis_results(),
            database_count=get_database_count(),
            pull_running=False,
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
