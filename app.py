import os
from datetime import timedelta

from dotenv import load_dotenv


APP_FILE_PATH = os.path.abspath(__file__)
PROJECT_DIR = os.path.dirname(APP_FILE_PATH)
ENV_PATH = os.path.join(PROJECT_DIR, ".env")

load_dotenv(ENV_PATH)


from flask import Flask, session, request, redirect, url_for, flash, jsonify

from routes.admin import admin_bp
from routes.main import main_bp

from db import init_db
from services.cart_service import get_cart_count
from services.csrf_service import validate_csrf_from_form, get_csrf_token

init_db()


app = Flask(__name__)
app.register_blueprint(admin_bp)
app.register_blueprint(main_bp)
app.permanent_session_lifetime = timedelta(days=1)

SECRET_KEY = os.environ.get('SECRET_KEY')

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY не задан")
    
app.secret_key = SECRET_KEY


@app.before_request
def protect_from_csrf():
    if request.method != "POST":
        return
        
    if validate_csrf_from_form():
        return 
        
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
        "success": False,
        "message": "Некорректный защитный токен формы"
        }), 400
        
    flash("Некорректный защитный токен формы", "error")
    return redirect(request.referrer or url_for("main.index"))


@app.context_processor
def inject_cart_count():
    """
Добавляет количество товаров в корзине во все шаблоны приложения.

Функция вызывается Flask автоматически перед рендерингом шаблонов благодаря
декоратору context_processor. Возвращает словарь с cart_count, чтобы в базовом
шаблоне можно было показывать актуальное количество товаров в корзине независимо
от того, какая страница открыта.
"""
    return {"cart_count": get_cart_count(session)}
    
    
@app.context_processor
def inject_csrf_token():
    return {"csrf_token": get_csrf_token}
    
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)