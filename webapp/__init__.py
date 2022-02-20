from flask import Flask, redirect, url_for
import os
from flask_apscheduler import APScheduler


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is not None:
        app.config.from_mapping(test_config)
    elif os.environ.get("FLASK_ENV", "production") == "production":
        app.config.from_object("webapp.config.ProductionConfig")
    else:
        app.config.from_object("webapp.config.DevelopmentConfig")
        app.config["DATABASE"] = os.path.join(app.instance_path,
                                              "webapp.sqlite")

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import products
    app.register_blueprint(products.bp)

    from . import db
    db.init_app(app)

    from . import scraper_facade
    scraper_facade.init_app(app)

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    @app.route("/")
    def home():
        return redirect(url_for("products.products_page"))
    return app


app = create_app()
