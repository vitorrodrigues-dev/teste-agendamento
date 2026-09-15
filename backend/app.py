from pathlib import Path

from flask import Flask

import config
from routes.appointments import appointments_bp
from routes.available import available_bp

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


def create_app():
    app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
    app.register_blueprint(available_bp)
    app.register_blueprint(appointments_bp)

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=config.FLASK_DEBUG)
