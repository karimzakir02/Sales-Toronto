from . import builders
from webapp.db import get_db
from flask.cli import with_appcontext
import click
import webapp


@click.command("scrape-data")
@with_appcontext
def get_items_command():
    get_items_facade()
    click.echo("Sucessfully retrieved the sales items for today")


def _duplicate_item(db, item):
    criteria = [item[0], item[1], item[7]]
    # name = item[0]
    # store = item[1]
    # date_ended = item[7]
    query = ('SELECT * FROM products WHERE name = ?'
             'AND original_store = ?'
             'AND date_ended = ?;')
    try:
        duplicate_items = db.execute(query, criteria).fetchall()
    except Exception:
        print(query)

    return len(duplicate_items) > 0


def _commit_to_db(items):
    db = get_db()
    for item in items:
        if not _duplicate_item(db, item):
            db.execute(
                ("INSERT INTO products(name, original_store, current_price,"
                 "old_price, link, package_size, date_started, date_ended)"
                 "VALUES(?, ?, ?, ?, ?, ?, ?, ?)"),
                item
            )
    db.commit()


def get_items_facade():

    items = []
    scrapers = builders.WebScraperBuilder.build_retrievers()

    for scraper in scrapers:
        items.extend(scraper.get_products())

    with webapp.app.app_context():
        _commit_to_db(items)


def init_app(app):
    app.cli.add_command(get_items_command)
