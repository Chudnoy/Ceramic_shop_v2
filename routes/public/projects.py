from flask import abort, render_template

from services.public_project_service import get_public_project_page_data

from . import public_bp


@public_bp.route("/projects/<slug>")
def project_detail(slug):
    page_data = get_public_project_page_data(slug)
    
    if page_data is None:
        abort(404)
        
    return render_template(
        "public/project.html",
        project=page_data["project"],
        images=page_data["images"],
        cover_image=page_data["cover_image"],
        project_works=page_data["project_works"]
    )