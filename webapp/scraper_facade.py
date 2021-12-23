from scrapers import LoblawsScraper
from webapp.db import get_db


def get_items_facade():
    items = []
    loblaws_scraper = LoblawsScraper()

    items.extend(loblaws_scraper.get_products())

    db = get_db()
    for item in items:
        db.execute(
            ("INSERT INTO products(name, original_store, current_price,
            old_price, in_stock, package_size) VALUES(?, ?, ?, ?, ?, ?)",
            item
        )
    db.commit()
