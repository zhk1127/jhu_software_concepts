"""Run the Module 6 Flask web service."""

import os

from src.web.app.app import create_app

flask_app = create_app()

if __name__ == "__main__":
    flask_app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
