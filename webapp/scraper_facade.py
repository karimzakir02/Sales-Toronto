from . import scraper_builder
from webapp.db import get_db
from flask.cli import with_appcontext
import click


@click.command("scrape-data")
@with_appcontext
def get_items_command():
    get_items_facade()
    click.echo("Sucessfully retrieved the sales items for today")


def get_items_facade():

    items = []
    scrapers = scraper_builder.build_scrapers()

    for scraper in scrapers:
        items.extend(scraper.get_products())

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
