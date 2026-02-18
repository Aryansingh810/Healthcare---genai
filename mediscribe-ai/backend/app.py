"""
MediScribe AI - Flask Application
Main entry point. Serves frontend and API routes.
"""

import os
from pathlib import Path

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from routes.store import store_bp
from routes.generate import generate_bp

# Load .env from backend directory
load_dotenv(Path(__file__).resolve().parent / ".env")

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "..", "frontend", "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "..", "frontend", "static")
)
CORS(app)

# Register API blueprints
app.register_blueprint(store_bp, url_prefix="/api")
app.register_blueprint(generate_bp, url_prefix="/api")


@app.route("/")
def index():
    """Landing page."""
    return render_template("index.html")


@app.route("/about")
def about():
    """About page."""
    return render_template("about.html")


@app.route("/workspace")
def workspace():
    """Workspace page."""
    return render_template("workspace.html")


@app.route("/assets/<path:filename>")
def assets(filename):
    """Static assets."""
    return send_from_directory(
        Path(app.static_folder) / "assets",
        filename
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
