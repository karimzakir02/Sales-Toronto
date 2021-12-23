from abc import ABC, abstractmethod
from seleniumwire import webdriver
import time
from seleniumwire.utils import decode
import json
from url_enums import StoreURLs


class Scraper(ABC):

    @abstractmethod
    def get_products(self):
        raise NotImplementedError


class LoblawsScraper(Scraper):

    def get_products(self):
        # the set-up could probably be factored into a facade class
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument('window-size=1400,2000')
        driver = webdriver.Chrome(options=options)
        driver.get(StoreURLs.LOBLAWS)
        time.sleep(5)
        get_height_command = "return document.body.scrollHeight"
        last_height = driver.execute_script(get_height_command)
        new_height = -1
        while last_height != new_height:
            last_height = new_height
            scroll_bottom = "window.scrollTo(0, document.body.scrollHeight);"
            driver.execute_script(scroll_bottom)
            time.sleep(1)
            new_height = driver.execute_script(get_height_command)

        LOBLAWS_POST_URL = ("https://api.pcexpress.ca/"
                            "product-facade/v3/products/deals")

        items = []
        for request in driver.requests:
            if request.url == LOBLAWS_POST_URL:
                response = request.response
                body = decode(response.body,
                              response.headers.get("Content-Encoding",
                                                   "identity"))
                json_body = json.loads(body.decode("utf-8"))
                items.extend(json_body["results"])

        processed_data = self.process_items(items)
        return processed_data

    def process_items(items):
        tuples = []
        for item in items:
            tup = (item["name"], "Loblaws", item["prices"]["price"]["value"],
                   item["prices"]["wasPrice"]["value"],
                   int(item["stockStatus"] == "OK"), item["packageSize"])
            tuples.append(tup)
        return tuples
