from . import scrapers
from webapp.db import get_db
from flask.cli import with_appcontext
import click
from seleniumwire import webdriver


@click.command("scrape-data")
@with_appcontext
def get_items_command():
    get_items_facade()
    click.echo("Sucessfully retrieved the sales items for today")


def get_items_facade():
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument("window-size=1400,2000")
    driver = webdriver.Chrome(options=options)

    items = []
    loblaws_scraper = scrapers.LoblawsScraper()

    items.extend(loblaws_scraper.get_products(driver))

    db = get_db()
    for item in items:
        db.execute(
            ("INSERT INTO products(name, original_store, current_price,"
             "old_price, in_stock, package_size, year, month, day)"
             "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"),
            item
        )
    db.commit()


def init_app(app):
    app.cli.add_command(get_items_command)
