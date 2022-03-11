import re
from datetime import date, datetime, timedelta

import requests

from .data_retriever_interface import DataRetrieverInterface


class SimpleWebScraper(DataRetrieverInterface):

    def __init__(self):
        pass


class SimpleMetroScraper(SimpleWebScraper):

    def __init__(self):
        super().__init__()
        self.STORE_NAME = "Metro"

        # Flyer page:
        self.FLYER_PAGE = "https://www.metro.ca/en/flyer"

        # URL from which the sales data is obtained:
        self.API_URL = ("https://dam.flippenterprise.net/flyerkit/"
                        "publication/{}/ products?display_type=all&"
                        "locale=en&access_token={}")

    def get_products(self):

        request_arguments = self._get_arguments()

        items = self._get_items(request_arguments)

    def _get_arguments(self):
        # Get the arguments required from the flyer page
        # to get the items currently on sale
        page_response = requests.get(self.FLYER_PAGE)

        if page_response.status_code != 200:
            return ""

        access_token = re.findall("var flippAccessToken = \"(\\w+)\";",
                                  page_response.text)[0]

        flyer_num = re.findall("var publicationsWeekStatus = {\"(\\d+)\":true")
        flyer_num = flyer_num[0]  # indexing moved to second line for pep8

        return access_token, flyer_num

    def _get_items(self, request_arguments):
        # Return the products from their API in a JSON format
        items_response = requests.get(self.API_URL.format(*request_arguments))

        if items_response.status_code != 200:
            return ""

        return items_response.json()
