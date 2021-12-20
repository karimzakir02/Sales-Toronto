from flask import (
    Blueprint,
)

bp = Blueprint("products", __name__, url_prefix="/products")


@bp.route("/")
def products_page():
    return "<p>Hello! This is my upcoming data engineering project!</p>"
