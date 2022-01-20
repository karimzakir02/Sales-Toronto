from abc import ABC, abstractmethod
import time
from seleniumwire.utils import decode
import json
from .url_enum import StoreURLs
from datetime import date, datetime
from seleniumwire import webdriver
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By



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
        self.METRO_API_URL = "ecirculaire.metro.ca/flyer_data/"
        self.METRO_OLD_PRICE_URL = ("https://www.metro.ca/en/flyer/"
                                    "getSelectedFlyerPromosDetails")

    def get_products(self):
        self.driver.get(StoreURLs.METRO)
        time.sleep(5)
        self._get_to_window()
        self.driver.save_screenshot("metro_screenshot.png")

        items = self._get_required_responses()

        processed_items = self._process_items(items)

        self.driver.quit()

        return processed_items

    def _get_to_window(self):
        frame = self.driver.find_element(By.ID, "flipp-iframe")
        self.driver.switch_to.frame(frame)
        button_xpath = ('//*[@id="other_flyer_runs"]/div/div/div/div[2]/'
                        'table/tbody/tr[1]')
        button = self.driver.find_element(By.XPATH, button_xpath)
        button.click()
        time.sleep(1)

    def _process_items(self, items):
        processed_data = []
        count = 0
        for item in items:
            print(count)
            if not self._item_valid(item):
                continue
            tup = (item["name"], "Metro", item["current_price"],
                   self._get_old_price(item), "", item["description"],
                   item["valid_from"], item["valid_to"])

            processed_data.append(tup)
            count += 1
        return processed_data

    def _item_valid(self, item):
        if item["current_price"] is None:
            return False
        return True

    def _get_old_price(self, item):
        valid_from = datetime.strptime(item["valid_from"], "%Y-%m-%d")
        valid_to = datetime.strptime(item["valid_to"], "%Y-%m-%d")

        json_params = {
            "from": valid_from.strftime("%Y%m%dT000000"),
            "to": valid_to.strftime("%Y%m%dT000000"),
            "blockId": item["sku"],
            "itemId": item["flyer_item_id"],
            "flyerRunId": item["flyer_run_id"]
        }

        response = requests.post(self.METRO_OLD_PRICE_URL, json=json_params)
        if response.status_code != 200:
            return 0
        else:
            old_price = self._find_old_price(response.text)
            # TODO: sometimes old price is smaller than current price.
            # Refer to the notes to check how to fix this.
            return old_price

    def _find_old_price(self, text_response):
        soup = BeautifulSoup(text_response, features="html.parser")
        price_div = soup.find(attrs={"class": "pi-regular-price"})

        if price_div is None:
            return 0

        price_txt = price_div.find(attrs={"class": "pi-price"}).text
        return float(price_txt[1:])

    def _get_required_responses(self):
        items = []
        for request in self.driver.requests:
            if self.METRO_API_URL in request.url:
                response = request.response
                body = decode(response.body,
                              response.headers.get("Content-Encoding",
                                                   "identity"))
                print(body)
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
