from flask import render_template
from database.stats import get_admin_stats

from . import admin_bp

@admin_bp.route("/admin")
def admin():
    """
Показывает главную страницу админки.

Получает статистику через get_admin_stats и передаёт её в шаблон admin/index.html.
Используется как стартовая панель управления магазином.
"""
    stats = get_admin_stats()
    return render_template("admin/index.html", stats=stats)