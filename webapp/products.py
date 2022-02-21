from flask import (
    Blueprint, render_template, flash
)
from webapp.db import get_db
from datetime import datetime
import random

bp = Blueprint("products", __name__, url_prefix="/products")


@bp.route("/")
def products_page():
    db = get_db()
    error = None
    today = datetime.today().strftime("%Y%m%d")
    items = db.execute(
        f"SELECT * FROM products WHERE date_ended >= {today}").fetchall()

    random.seed(2022)
    random.shuffle(items)

    if error is not None:
        flash(error)

    return render_template("products/products.html", items=items)
