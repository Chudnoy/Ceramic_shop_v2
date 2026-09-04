from flask import Blueprint

public_bp = Blueprint("public", __name__, url_prefix="/v2")

from . import home, works
