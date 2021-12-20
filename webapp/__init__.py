from flask import Flask, redirect, url_for
import os


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "webapp.sqlite"),
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import products
    app.register_blueprint(products.bp)

    from . import db
    db.init_app(app)

    @app.route("/")
    def home():
        return redirect(url_for("products.products_page"))
    return app
