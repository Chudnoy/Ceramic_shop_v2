import os
from datetime import timedelta

from dotenv import load_dotenv

APP_FILE_PATH = os.path.abspath(__file__)
PROJECT_DIR = os.path.dirname(APP_FILE_PATH)
ENV_PATH = os.path.join(PROJECT_DIR, ".env")

# /storage/emulated/0/Ceramic_shop_v2

load_dotenv(ENV_PATH)


from flask import Flask, flash, jsonify, redirect, request, session, url_for

from database.schema import init_db
from routes.admin import admin_bp
from routes.main import main_bp
from services.cart_service import get_cart_count
from services.csrf_service import get_csrf_token, validate_csrf_from_form


def create_app(test_config=None):
    app = Flask(__name__)

    app.permanent_session_lifetime = timedelta(days=1)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        ADMIN_LOGIN=os.environ.get("ADMIN_LOGIN"),
        ADMIN_PASSWORD_HASH=os.environ.get("ADMIN_PASSWORD_HASH"),
        DATABASE=os.path.join(PROJECT_DIR, "shop.db"),
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY не задан")

    if not app.config["ADMIN_LOGIN"]:
        raise RuntimeError("ADMIN_LOGIN не задан")

    if not app.config["ADMIN_PASSWORD_HASH"]:
        raise RuntimeError("ADMIN_PASSWORD_HASH не задан")

    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)

    @app.before_request
    def protect_from_csrf():
        if request.method != "POST":
            return

        if validate_csrf_from_form():
            return

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(
                {"success": False, "message": "Некорректный защитный токен формы"}
            ), 400

        flash("Некорректный защитный токен формы", "error")
        return redirect(request.referrer or url_for("main.index"))

    @app.context_processor
    def inject_cart_count():
        return {"cart_count": get_cart_count(session)}

    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": get_csrf_token}

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        init_db()
    app.run(host="0.0.0.0", port=8000, debug=True)
