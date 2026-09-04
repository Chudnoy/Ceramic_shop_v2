from flask import abort, render_template

from services.public_work_service import get_public_work_page_data

from . import public_bp


@public_bp.route("/works/<slug>")
def work_detail(slug):
    page_data = get_public_work_page_data(slug)

    if page_data is None:
        abort(404)

    return render_template(
        "public/work.html",
        work=page_data["work"],
        images=page_data["images"],
        categories=page_data["categories"],
        tags=page_data["tags"],
        materials=page_data["materials"],
        shop_item=page_data["shop_item"],
    )
