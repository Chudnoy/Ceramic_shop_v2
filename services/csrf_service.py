import secrets

from flask import request, session


def get_csrf_token():
    """
    Возвращает CSRF-токен для текущей session.
    
    Если токена ещё нет в session, создаёт новый случайный токен и сохраняет его.
    Один и тот же токен потом используется во всех формах текущей session.
    """
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    
    return session["csrf_token"]
    
    
def validate_csrf_token(token):
    """
    Проверяет CSRF-токен, пришедший из формы.
    
    Возвращает True, если токен есть и совпадает с токеном, сохраненным в session.
    Возвращает False, если токена нет, он пустой или не совпадает.
    """
    return token and token == session.get("csrf_token")
    
    
def validate_csrf_from_form():
    """
    Проверяет CSRF-токен из текущей POST-формы.
    
    Достаёт csrf-токен из request.form и сравнивает его с токеном, сохранённым в session. Возвращает True, если токен корректен, иначе False.
    """
    token = request.form.get("csrf_token")
    return validate_csrf_token(token)