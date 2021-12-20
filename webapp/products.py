from flask import (
    Blueprint, render_template
)

bp = Blueprint("products", __name__, url_prefix="/products")


@bp.route("/")
def products_page():
    return render_template("products/products.html")
