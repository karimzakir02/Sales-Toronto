from .selenium_webscraper import SeleniumWebscraper
from seleniumwire.utils import decode
import time
from datetime import date, datetime
import json


class LoblawsSeleniumWebscraper(SeleniumWebscraper):

    def __init__(self):
        super().__init__()
        self.LOBLAWS_API_URL = ("https://api.pcexpress.ca/"
                                "product-facade/v3/products/deals")
        self.STORE_NAME = "Loblaws"
        self.STORE_URL = ("https://www.loblaws.ca/deals/all?sort=relevance&"
                          "category=27985&promotions=Price%20Reduction")

    def get_products(self):
        self.driver.get(self.STORE_URL)
        time.sleep(5)

        self._scroll_down()
        # self.driver.save_screenshot("loblaws_sc.png")
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
            tup = (item["name"], self.STORE_NAME,
                   item["prices"]["price"]["value"],
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
