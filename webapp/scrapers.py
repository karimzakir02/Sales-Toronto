from abc import ABC, abstractmethod
import time
from seleniumwire.utils import decode
import json
from .url_enum import StoreURLs
from datetime import date, datetime
from seleniumwire import webdriver
import requests
from bs4 import BeautifulSoup


class Scraper(ABC):

    def __init__(self):
        # Each scraper will have its own webdriver to allow for easier
        # asynchronous scraping in the future
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("window-size=1400,2000")
        self.driver = webdriver.Chrome(options=options)

    @abstractmethod
    def get_products(self):
        raise NotImplementedError


class MetroScraper(Scraper):

    def __init__(self):
        super().__init__()
        self.METRO_API_URL = ("https://ecirculaire.metro.ca/"
                              "flyer_data/4561334?locale=en")
        self.METRO_OLD_PRICE_URL = ("https://www.metro.ca/en/flyer/"
                                    "getSelectedFlyerPromosDetails")

    def get_products(self):
        self.driver.get(StoreURLs.METRO)
        time.sleep(5)

        items = self._get_required_responses()

        processed_items = self._process_items(items)

        return processed_items

    def _process_items(self, items):
        processed_data = []

        for item in items:
            tup = (item["name"], "Metro", item["current_price"],
                   self._get_old_price(item), "", item["valid_from"],
                   item["valid_to"], item["description"])

            processed_data.append(tup)
        return processed_data

    def _get_old_price(self, item):
        valid_from = datetime.strptime(item["valid_from"], "%Y-%m-%d")
        valid_to = datetime.strptime(item["valid_to"], "%Y-%m-%d")

        json_params = {
            "from": valid_from.strftime("%Y%m%dT000000"),
            "to": valid_to.strftime("%Y%m%dT000000"),
            "blockId": item["sku"],
            "itemId": item["flyer_item_id"],
            "flyer_run_id": item["flyer_run_id"],
        }

        response = requests.post(self.METRO_OLD_PRICE_URL, json_params)
        soup = BeautifulSoup(response.text, features="html.parser")
        if response.status_code != 200:
            return 0
        price_div = soup.find(attrs={"class": "pi-regular-price"})
        price_txt = price_div.find(attrs={"class": "pi-price"}).text
        return float(price_txt[1:])

    def _get_required_responses(self):
        items = []
        for request in self.driver.requests:
            if request.url == self.METRO_API_URL:
                response = request.response
                body = decode(response.body,
                              response.headers.get("Content-Encoding",
                                                   "identity"))
                json_body = json.loads(body.decode("utf-8"))
                items.extend(json_body["items"])
        return items


class LoblawsScraper(Scraper):

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
                body = decode(response.body,
                              response.headers.get("Content-Encoding",
                                                   "identity"))
                json_body = json.loads(body.decode("utf-8"))
                items.extend(json_body["results"])
        return items
