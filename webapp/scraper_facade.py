from request_webscrapers import Builder
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
    query = ('SELECT * FROM products WHERE name = ?'
             'AND original_store = ?'
             'AND date_ended = ?;')

    duplicate_items = db.execute(query, criteria).fetchall()

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
    scrapers = Builder.build_retrievers()

    for scraper in scrapers:
        try:
            items.extend(scraper.get_products())
        except Exception as e:
            webapp.app.logger.error(
                f"Error occured for {scraper.STORE_NAME}: {str(e)}")

    with webapp.app.app_context():
        _commit_to_db(items)


def init_app(app):
    app.cli.add_command(get_items_command)
