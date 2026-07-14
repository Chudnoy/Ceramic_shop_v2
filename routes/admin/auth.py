import os
from flask import session, request, redirect, url_for, flash, render_template
from werkzeug.security import check_password_hash

from . import admin_bp

ADMIN_LOGIN = os.environ.get("ADMIN_LOGIN")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH")

if not ADMIN_LOGIN:
    raise RuntimeError("ADMIN_LOGIN не задан")

if not ADMIN_PASSWORD_HASH:
    raise RuntimeError("ADMIN_PASSWORD_HASH не задан")

@admin_bp.before_request
def require_admin_login():
    """
Проверяет доступ к админским маршрутам перед каждым запросом.

Разрешает открывать страницу логина без авторизации. Для остальных admin routes
проверяет наличие session["is_admin"]. Если пользователь не авторизован как админ,
показывает flash-сообщение и перенаправляет на страницу входа.
"""
    allowed_endpoints = {
        'admin.login'
    }

    if request.endpoint in allowed_endpoints:
        return
    
    if session.get('is_admin'):
        return
    
    flash('Сначала войдите в админку', 'error')
    return redirect(url_for('admin.login'))


@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    """
Обрабатывает вход в админку.

При GET-запросе показывает форму входа. При POST-запросе проверяет логин и пароль
по значениям из переменных окружения. Если данные верны, сохраняет признак
администратора в session и перенаправляет на главную страницу админки.
"""
    if request.method == 'POST':
        login_value = request.form.get('login', '').strip()
        password = request.form.get('password', '')

        if login_value == ADMIN_LOGIN and ADMIN_PASSWORD_HASH and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session.permanent = True
            session['is_admin'] = True
            flash('Вы вошли в админку', 'success')
            return redirect(url_for('admin.admin'))
        
        flash('Неверный логин или пароль', 'error')
    return render_template('admin/login.html')


@admin_bp.route('/admin/logout', methods=['POST'])
def logout():
    """
Выводит пользователя из админки.

Удаляет флаг is_admin из session, показывает flash-сообщение и перенаправляет
пользователя на страницу входа в админку.
"""
    session.pop('is_admin', None)
    flash('Вы вышли из админки', 'info')
    return redirect(url_for('admin.login'))