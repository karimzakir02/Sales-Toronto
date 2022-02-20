import os
from datetime import datetime, timedelta
from .scraper_facade import get_items_facade


class Config(object):
    TESTING = False

    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "US/Eastern"


class ProductionConfig(Config):
    SECRET_KEY = os.environ.get("SECRET_KEY")

    if not SECRET_KEY and os.environ.get("FLASK_ENV") == "production":
        raise ValueError("SECRET_KEY was not set for this application")

    START_DATE = (datetime.today() + timedelta(days=1)).replace(hour=0,
                                                                minute=1,
                                                                second=0)
    JOBS = [
        {
            "id": "get_items",
            "func": get_items_facade,
            "trigger": "interval",
            "days": 1,
            "start_date": START_DATE,
        },
    ]


class DevelopmentConfig(Config):
    SECRET_KEY = "dev"

    START_DATE = datetime.today() + timedelta(seconds=10)
    JOBS = [
        {
            "id": "get_items",
            "func": get_items_facade,
            "trigger": "interval",
            "days": 1,
            "start_date": START_DATE,
        },
    ]
