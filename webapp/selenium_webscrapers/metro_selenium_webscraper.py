from .selenium_webscraper import SeleniumWebscraper
from seleniumwire.utils import decode
import time
from datetime import datetime, timedelta
import requests
import bs4
from bs4 import BeautifulSoup
import json


class MetroSeleniumWebscraper(SeleniumWebscraper):

    def __init__(self):
        super().__init__()
        self.METRO_API_URL = "dam.flippenterprise.net/flyerkit/publication"
        self.METRO_OLD_PRICE_URL = ("https://www.metro.ca/en/flyer/"
                                    "getSelectedFlyerPromosDetails")
        self.LINK = "https://www.metro.ca/en/flyer"
        self.STORE_NAME = "Metro"
        self.STORE_URL = "https://www.metro.ca/en/flyer"

    def get_products(self):
        self.driver.get(self.STORE_URL)
        time.sleep(5)
        items = self._get_required_responses()

        processed_items = self._process_items(items)

        self.driver.quit()

        return processed_items

    def _process_items(self, items):
        processed_data = []
        for item in items:
            if not self._item_valid(item):
                continue

            self._modify_dates(item)
            old_price = self._get_old_price(item)
            tup = (item["name"], self.STORE_NAME, item["current_price"],
                   old_price, self.LINK, item["description"],
                   item["valid_from"], item["valid_to"])

            processed_data.append(tup)
        return processed_data

    def _modify_dates(self, item):
        valid_from = datetime.strptime(item["valid_from"], "%Y-%m-%d")
        item["valid_from"] = valid_from.strftime("%Y%m%d")
        valid_to = datetime.strptime(item["valid_to"], "%Y-%m-%d")
        item["valid_to"] = valid_to.strftime("%Y%m%d")

    def _item_valid(self, item):
        # Some items are recipes, which don't have a price tag
        if item.get("current_price") is None:
            return False
        return True

    def _get_old_price(self, item):
        valid_from = datetime.strptime(item["valid_from"], "%Y%m%d")
        valid_to = datetime.strptime(item["valid_to"], "%Y%m%d")
        valid_to = valid_to + timedelta(days=1)

        json_params = {
            "from": valid_from.strftime("%Y-%m-%dT05:00:00.000Z"),
            "to": valid_to.strftime("%Y-%m-%dT04:59:59.999Z"),
            "blockId": item["sku"],
            "itemId": item["id"],
            "flyerRunId": item["flyer_run_id"]
        }

        response = requests.post(self.METRO_OLD_PRICE_URL, json=json_params)
        if response.status_code != 200:
            return 0
        else:
            old_price = self._find_old_price(item, response.text)
            return old_price

    def _find_old_price(self, item, text_response):
        soup = BeautifulSoup(text_response, features="html.parser")
        regular_price_div = soup.find(attrs={"class": "pi-regular-price"})

        if regular_price_div is None:
            return 0

        price_txt = regular_price_div.find(attrs={"class": "pi-price"})
        if price_txt is None:
            return 0
        else:
            price = self._adjust_sale_price(soup)
            item["current_price"] = price if price else item["current_price"]
            return float(price_txt.text[1:])

    def _adjust_sale_price(self, soup):
        # Sometimes, the old price is provided in different units than the
        # sale price, so this function searches for the appropriate sale price
        units = ["Kilogram", "Each", "Pound"]
        regular_price_div = soup.find(attrs={"class": "pi-regular-price"})
        old_price_unit_tag = regular_price_div.find(attrs={"class": "pi-unit"})

        for node in old_price_unit_tag:
            if type(node) == bs4.element.Tag and node.attrs["title"] in units:
                required_unit = node.attrs["title"]

        sale_price_div = soup.find(attrs={"class": "pi-sale-price"})
        sale_unit = sale_price_div.find(attrs={"class":
                                               "pi-unit pi-price-promo"})
        if sale_unit and \
                sale_unit.find(attrs={"title": required_unit}) is not None:
            price = sale_price_div.find(attrs={"class": "pi-price"})
            return float(price.text[1:])

        secondary_price = soup.find(attrs={"class": "pi-secondary-price"})
        prices = secondary_price.find_all(attrs={"class": "pi-price"})
        for price in prices:
            if price.find(attrs={"title": required_unit}) is not None:
                price_string = price.contents[0]
                return float(price_string[1: len(price_string) - 1])

        return 0

    def _get_required_responses(self):
        items = []
        for request in self.driver.requests:
            if self.METRO_API_URL in request.url:
                response = request.response
                if response is None:
                    continue
                body = decode(response.body,
                              response.headers.get("Content-Encoding",
                                                   "identity"))
                json_body = json.loads(body.decode("utf-8"))
                items.extend(json_body)
        return items
