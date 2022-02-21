from .data_retriever_interface import DataRetrieverInterface
import time
from seleniumwire.utils import decode
import json
from .url_enum import StoreURLs
from datetime import date, datetime
from seleniumwire import webdriver
import requests
import bs4
from bs4 import BeautifulSoup


class WebScraper(DataRetrieverInterface):

    def __init__(self):
        # Each scraper will have its own webdriver to allow for easier
        # asynchronous scraping in the future
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("window-size=1400,2000")
        self.driver = webdriver.Chrome(options=options)


class FreshcoScraper(WebScraper):

    def __init__(self):
        super().__init__()
        self.FRESH_API_URL = "https://dam.flippenterprise.net"

    def get_products(self):
        self.driver.get(StoreURLs.FRESHCO)
        time.sleep(5)

        items = self._get_required_responses()

        processed_items = self._process_items(items)

        self.driver.quit()

        return processed_items

    def _item_valid(self, item):
        if item.get("current_price") is None:
            return False
        return True

    def _adjust_old_price(self, item):
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
            tup = (item["name"], "FreshCo", item["current_price"],
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


class MetroScraper(WebScraper):

    def __init__(self):
        super().__init__()
        self.METRO_API_URL = "dam.flippenterprise.net/flyerkit/publication"
        self.METRO_OLD_PRICE_URL = ("https://www.metro.ca/en/flyer/"
                                    "getSelectedFlyerPromosDetails")
        self.LINK = "https://www.metro.ca/en/flyer"

    def get_products(self):
        self.driver.get(StoreURLs.METRO)
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
            tup = (item["name"], "Metro", item["current_price"],
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

        json_params = {
            "from": valid_from.strftime("%Y%m%dT000000"),
            "to": valid_to.strftime("%Y%m%dT000000"),
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


class LoblawsScraper(WebScraper):

    def __init__(self):
        super().__init__()
        self.LOBLAWS_API_URL = ("https://api.pcexpress.ca/"
                                "product-facade/v3/products/deals")

    def get_products(self):
        self.driver.get(StoreURLs.LOBLAWS)
        time.sleep(5)

        self._scroll_down()

        items = self._get_required_responses()
        processed_data = self._process_items(items)

        self.driver.quit()

        return processed_data

    def _process_items(self, items):
        # Prepare data to be added to the database
        processed_data = []
        for item in items:
            link = "https://www.loblaws.ca" + item["link"]
            expiry_date_txt = item["badges"]["dealBadge"]["expiryDate"]
            expiry_date = datetime.strptime(expiry_date_txt[:10], "%Y-%m-%d")
            expiry_date_str = expiry_date.strftime("%Y%m%d")
            tup = (item["name"], "Loblaws", item["prices"]["price"]["value"],
                   item["prices"]["wasPrice"]["value"], link,
                   item["packageSize"], date.today().strftime("%Y%m%d"),
                   expiry_date_str)
            processed_data.append(tup)
        return processed_data

    def _scroll_down(self):
        # Scroll down to the bottom of the page to load all offers
        get_height_command = "return document.body.scrollHeight"
        last_height = self.driver.execute_script(get_height_command)
        new_height = -1
        while last_height != new_height:
            last_height = new_height
            scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
            self.driver.execute_script(scroll_down)
            time.sleep(1)
            new_height = self.driver.execute_script(get_height_command)

    def _get_required_responses(self):
        # Only decode and return responses that came from their deals POST API
        items = []
        for request in self.driver.requests:
            if request.url == self.LOBLAWS_API_URL:
                response = request.response
                if response is None:
                    continue
                body = decode(response.body,
                              response.headers.get("Content-Encoding",
                                                   "identity"))
                json_body = json.loads(body.decode("utf-8"))
                items.extend(json_body["results"])
        return items
