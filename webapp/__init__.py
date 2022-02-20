from flask import Flask, redirect, url_for
import os
from flask_apscheduler import APScheduler
from datetime import datetime, timedelta
from .scraper_facade import get_items_facade


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    start_date = datetime.today() + timedelta(seconds=20)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "webapp.sqlite"),
        SCHEDULER_API_ENABLED=True,
        JOBS=[{
            "id": "job1",
            "func": get_items_facade,
            "args": (app,),
            "trigger": "interval",
            "days": 1,
            "start_date": start_date
        }],
        SCHEDULER_TIMEZONE="US/Eastern"
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

    from . import scraper_facade
    scraper_facade.init_app(app)

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    @app.route("/")
    def home():
        return redirect(url_for("products.products_page"))
    return app
