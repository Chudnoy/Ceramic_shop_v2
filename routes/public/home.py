from flask import render_template

from services.public_home_service import get_home_page_data

from . import public_bp


@public_bp.route("/")
def home():
    homepage_data = get_home_page_data()
    return render_template(
        "public/home.html",
        works=homepage_data["works"],
        shop_items=homepage_data["shop_items"],
    )
