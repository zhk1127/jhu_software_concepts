from flask import Flask, render_template, redirect, url_for
import subprocess
import sys
import psycopg

from query_data import get_analysis_results, DB_CONFIG

app = Flask(__name__)

pull_process = None


def pull_running():
    global pull_process

    if pull_process is None:
        return False

    if pull_process.poll() is None:
        return True

    pull_process = None
    return False


def get_database_count():
    conn = psycopg.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM applicants;")
    count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return count


@app.route("/")
def home():
    is_running = pull_running()

    if is_running:
        pull_status = (
            "Pull Data is currently running. "
            "The app is scraping approximately 500 additional GradCafe records "
            "and inserting new records into PostgreSQL."
        )
    else:
        pull_status = (
            "No data pull is currently running. "
            "New data has been added if available. "
            "Results are ready for analysis."
        )

    return render_template(
        "index.html",
        results=get_analysis_results(),
        database_count=get_database_count(),
        pull_running=is_running,
        pull_status=pull_status,
        message="",
    )


@app.route("/pull-data", methods=["POST"])
def pull_data():
    global pull_process

    if pull_running():
        return redirect(url_for("home"))

    pull_process = subprocess.Popen(
        [sys.executable, "-u", "pull_new_data.py"]
    )

    return redirect(url_for("home"))


@app.route("/update-analysis", methods=["POST"])
def update_analysis():
    if pull_running():
        return redirect(url_for("home"))

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)