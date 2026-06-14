from flask import Flask, render_template, redirect, url_for, jsonify
import subprocess
import sys

from src.query_data import get_analysis_results
from src.load_data import get_database_count


def create_app(config=None):
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    app.config.update(
        TESTING=False,
        PULL_PROCESS=None,
        CACHED_RESULTS=None,
        SCRAPER_COMMAND=[sys.executable, "-u", "src/pull_new_data.py"],
    )

    if config:
        app.config.update(config)

    def pull_running():
        process = app.config.get("PULL_PROCESS")

        if process is None:
            return False

        if process.poll() is None:
            return True

        app.config["PULL_PROCESS"] = None
        return False

    def get_cached_results():
        if app.config.get("CACHED_RESULTS") is None:
            app.config["CACHED_RESULTS"] = get_analysis_results()

        return app.config["CACHED_RESULTS"]

    @app.route("/")
    def home():
        return redirect(url_for("analysis"))

    @app.route("/analysis")
    def analysis():
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

    @app.route("/pull-data", methods=["POST"])
    def pull_data():
        if pull_running():
            return jsonify({"busy": True}), 409

        process = subprocess.Popen(app.config["SCRAPER_COMMAND"])
        app.config["PULL_PROCESS"] = process

        return jsonify({"ok": True}), 200

    @app.route("/update-analysis", methods=["POST"])
    def update_analysis():
        if pull_running():
            return jsonify({"busy": True}), 409

        app.config["CACHED_RESULTS"] = get_analysis_results()
        return jsonify({"ok": True}), 200

    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True)
