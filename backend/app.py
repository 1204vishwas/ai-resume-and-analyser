"""Flask application entry point for the AI Resume Analyzer backend."""
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from routes.api import api
from routes.auth import auth_api


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)  # allow the React dev server to call the API

    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(auth_api, url_prefix="/api/auth")

    @app.get("/")
    def index():
        return jsonify({
            "service": "AI Resume Analyzer API",
            "endpoints": ["/api/health", "/api/stats", "/api/roles", "/api/analyze"],
        })

    @app.errorhandler(413)
    def too_large(_e):
        return jsonify({"error": "File too large. Maximum size is 5 MB."}), 413

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
