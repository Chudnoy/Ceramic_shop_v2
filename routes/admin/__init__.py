from flask import Blueprint

admin_bp = Blueprint("admin", __name__)

from . import auth
from . import dashboard
from . import orders
from . import categories
from . import tags