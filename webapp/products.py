from flask import (
    Blueprint, render_template, flash
)
from webapp.db import get_db

bp = Blueprint("products", __name__, url_prefix="/products")


@bp.route("/")
def products_page():
    db = get_db()
    error = None

    items = db.execute(
        "SELECT * FROM products").fetchall()

    if error is not None:
        flash(error)

    return render_template("products/products.html", items=items)
