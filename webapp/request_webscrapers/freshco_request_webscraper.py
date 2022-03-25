from .request_webscraper import RequestWebscraper
import requests
import re


class FreshcoRequestWebscraper(RequestWebscraper):

    def __init__(self):
        super().__init__()

        self.STORE_NAME = "FreshCo"

        self.FLYER_PAGE = "https://freshco.com/flyer/"

        self.FLIPP_API_URL = ("https://dam.flippenterprise.net/flyerkit/"
                              "publications/Freshco?locale=en&access_token={}&"
                              "show_storefronts=true&store_code=9679")

        self.API_URL = ("https://dam.flippenterprise.net/flyerkit/publication/"
                        "{}/products?display_type=all&locale=en&"
                        "access_token={}")

    def get_products(self):

        access_token = self._get_access_token()

        flyer_num = self._get_flyer_num(access_token)

        items = self._get_items(flyer_num, access_token)

        processed_items = self._process_items(items)

        return processed_items

    def _get_access_token(self):

        headers = {'User-Agent':
                   ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
                    'AppleWebKit/537.36 (KHTML, like Gecko)'
                    'Chrome/50.0.2661.102 Safari/537.36')}

        flyer_page = requests.get(self.FLYER_PAGE, headers=headers)

        if flyer_page.status_code != 200:
            return ""

        access_token = re.findall('"accessToken":"([\\w]*)"')[0]
        return access_token

    def _get_flyer_num(self, access_token):
        page_response = requests.get(self.FLIPP_API_URL.format(access_token))

        if page_response.status_code != 200:
            return ""

        response = page_response.json()
        return response[0]["id"]

    def _get_items(self, flyer_num, access_token):
        items_response = requests.get(self.API_URL.format(flyer_num,
                                                          access_token))

        if items_response.status_code != 200:
            return ""

        return items_response.json()

    def _process_items(self, items):
        processed_items = []

        for item in items:
            if item["current_price"] is None:
                continue

            self._get_old_price(item)

            valid_from = item["valid_from"].replace("-", "")
            valid_to = item["valid_to"].replace("-", "")

            tup = (item["name"], self.STORE_NAME,
                   item["current_price"], item["original_price"],
                   self.FLYER_PAGE, None, valid_from, valid_to)
            processed_items.append(tup)

        return processed_items

    def _get_old_price(self, item):
        if item["original_price"] is not None:
            return

        if item["dollars_off"] is not None:
            item["original_price"] = item["current_price"] + \
                                        item["dollars_off"]
            return

        item["original_price"] = 0
