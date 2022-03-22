from .selenium_webscraper import SeleniumWebscraper
from seleniumwire.utils import decode
import time
from datetime import datetime
import json


class FreshcoSeleniumWebscraper(SeleniumWebscraper):

    def __init__(self):
        super().__init__()
        self.FRESH_API_URL = "https://dam.flippenterprise.net"
        self.STORE_NAME = "FreshCo"
        self.STORE_URL = "https://freshco.com/flyer/"

    def get_products(self):
        self.driver.get(self.STORE_URL)
        time.sleep(5)

        items = self._get_required_responses()

        processed_items = self._process_items(items)

        self.driver.quit()

        return processed_items

    def _item_valid(self, item):
        # Some items don't have current price,
        # making them unsuitable for our database
        if item.get("current_price") is None:
            return False
        return True

    def _adjust_old_price(self, item):
        # If an item misses its original price,
        # it's possible to obtain it as displayed here:
        if item.get("original_price") is None and \
                    item.get("dollars_off") is not None:
            item["original_price"] = float(item["current_price"]) + \
                                       float(item["dollars_off"])
        else:
            item["original_price"] = 0

    def _process_items(self, items):
        processed_data = []

        for item in items:
            if not self._item_valid(item):
                continue
            if item["original_price"] is None:
                self._adjust_old_price(item)

            self._modify_dates(item)

            link = "https://freshco.com/flyer/"
            tup = (item["name"], self.STORE_NAME, item["current_price"],
                   item["original_price"], link, "NaN", item["valid_from"],
                   item["valid_to"])

            processed_data.append(tup)

        return processed_data

    def _modify_dates(self, item):
        valid_from = datetime.strptime(item["valid_from"], "%Y-%m-%d")
        item["valid_from"] = valid_from.strftime("%Y%m%d")
        valid_to = datetime.strptime(item["valid_to"], "%Y-%m-%d")
        item["valid_to"] = valid_to.strftime("%Y%m%d")

    def _get_required_responses(self):
        items = []
        for request in self.driver.requests:
            if (self.FRESH_API_URL in request.url) & \
                                    ("products" in request.url):
                response = request.response
                if response is None:
                    continue
                body = decode(response.body,
                              response.headers.get("Content-Encoding",
                                                   "identity"))
                json_body = json.loads(body.decode("utf-8"))
                items.extend(json_body)
        return items
