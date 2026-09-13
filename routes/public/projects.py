from flask import abort, render_template, request

from services.public_project_service import get_public_project_page_data,get_public_projects_page_data

from . import public_bp


@public_bp.route("/projects/<slug>")
def project_detail(slug):
    page_data = get_public_project_page_data(slug)

    if page_data is None:
        abort(404)

    return render_template(
        "public/project.html",
        project=page_data["project"],
        project_paragraphs=page_data["project_paragraphs"],
        cover_image=page_data["cover_image"],
        premise_image=page_data["premise_image"],
        break_image=page_data["break_image"],
        process_image=page_data["process_image"],
        field_images=page_data["field_images"],
        project_works=page_data["project_works"],
    )


@public_bp.route("/projects")
def projects_index():
    sort = request.args.get("sort", "name_asc")
    
    page_data = get_public_projects_page_data(sort)
    
    return render_template("public/projects.html", projects=page_data["projects"], sort=sort)