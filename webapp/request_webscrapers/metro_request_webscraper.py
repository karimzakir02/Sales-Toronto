from .request_webscraper import RequestWebscraper
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


class SimpleMetroScraper(RequestWebscraper):

    def __init__(self):
        super().__init__()

        # Constant Attributes we will need later:

        self.STORE_NAME = "Metro"

        # Flyer page:
        self.FLYER_PAGE = "https://www.metro.ca/en/flyer"

        # URL from which the sales data is obtained:
        self.API_URL = ("https://dam.flippenterprise.net/flyerkit/"
                        "publication/{}/ products?display_type=all&"
                        "locale=en&access_token={}")

        # URL for the page containing an item's details
        self.ITEM_DETAILS_URL = ("https://www.metro.ca/en/flyer/"
                                 "getSelectedFlyerPromosDetails")

        # Shortened units used to find old price:
        self.SHORTENED_UNITS = ["/kg", "/lb", "avg. ea\\.", "ea\\.",
                                "/100g", "/100ml"]

    def get_products(self):

        request_arguments = self._get_arguments()

        items = self._get_items(request_arguments)

        processed_items = self._process_items(items)

        return processed_items

    def _get_arguments(self):
        # Get the arguments required by the flyer page
        # to get the items currently on sale
        page_response = requests.get(self.FLYER_PAGE)

        if page_response.status_code != 200:
            return ("", "")

        access_token = re.findall("var flippAccessToken = \"(\\w+)\";",
                                  page_response.text)[0]

        flyer_num = re.findall("var publicationsWeekStatus = {\"(\\d+)\":true")
        flyer_num = flyer_num[0]  # indexing moved to second line for pep8

        return access_token, flyer_num

    def _get_items(self, request_arguments):
        # Get the products from their API in JSON format
        items_response = requests.get(self.API_URL.format(*request_arguments))

        if items_response.status_code != 200:
            return ""

        return items_response.json()

    def _process_items(self, items):
        # Process the data to ensure it fits into the database's schema
        processed_data = []

        for item in items:
            # Some 'items' are recipes and are not appropriate for our data:
            if not self._item_valid(item):
                continue

            if item["original_price"] is None:
                self._find_prices(item)

            item["valid_from"] = item["valid_from"].replace("-", "")
            item["valid_to"] = item["valid_to"].replace("-", "")

            tup = (item["name"], self.STORE_NAME, item["current_price"],
                   item["original_price"], self.FLYER_PAGE,
                   item["description"], item["valid_from"], item["valid_to"])

            processed_data.append(tup)

        return processed_data

    def _item_valid(self, item):
        if item.get("current_price") is None:
            return False
        return True

    def _find_prices(self, item):
        # We find the prices in the item's page
        # Sometimes, the item page displays multiple current prices
        # for different package sizes. This function finds old and new
        # prices that correspond to the same packaging size
        found = False

        page_text = self._get_page_text(item)

        for unit in self.SHORTENED_UNITS:
            to_find = f"\\$[\\d]+[^\\$]*{unit}"
            # Regex Expression without extra slashes: \$[\d]+[^\$]*{unit}

            matches = re.findall(to_find, page_text)
            if len(matches) == 2:
                # Two matches indicates a pair of old price and current price
                # for the same package size
                found = True
                break

        if not found:
            return

        item["current_price"] = float(matches[0][1:])
        item["original_price"] = float(matches[1][1:])

    def _get_page_text(self, item):
        # Item page contains information about current and old prices
        valid_to_date = datetime.strptime(item["valid_to"], "%Y-%m-%d")
        valid_to_date = valid_to_date + timedelta(days=1)
        valid_to = valid_to_date.strftime("%Y-%m-%d")

        # This seems to change with Daylight savings Time
        # Should probably handle this in the foreseeable future
        json_params = {
            "from": f"{item['valid_from']}T04:00:00.000Z",
            "to": f"{valid_to}T03:59:59.999Z",
            "blockId": item["sku"],
            "itemId": item["id"],
            "flyerRunId": item["flyer_run_id"],
        }

        item_page = requests.POST(self.ITEM_DETAILS_URL, json=json_params)

        if item_page.status_code != 200:
            return ""  # need to come up with a custom exceptions class

        soup = BeautifulSoup(item_page.content)
        text = soup.get_text().replace(" ", "").replace("\n", "")
        return text
