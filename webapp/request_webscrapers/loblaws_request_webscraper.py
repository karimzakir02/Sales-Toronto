from .request_webscraper import RequestWebscraper
import requests
from datetime import datetime, date


class LoblawsRequestWebscraper(RequestWebscraper):

    def __init__(self):
        super().__init__()

        self.STORE_NAME = "Loblaws"

        self.API_URL = ("https://api.pcexpress.ca/product-facade/"
                        "v3/products/deals")

        self.X_API_KEY = "1im1hL52q9xvta16GlSdYDsTsG0dmyhF"

    def get_products(self):

        items = self._get_items()

        processed_items = self._process_items(items)

        return processed_items

    def _process_items(self, items):
        processed_data = []

        for item in items:
            link = "https://www.loblaws.ca" + item["link"]
            expiry_date_txt = item["badges"]["dealBadge"]["expiryDate"][:10]
            expiry_date = expiry_date_txt.replace("-", "")

            tup = (item["name"], self.STORE_NAME,
                   item["prices"]["price"]["value"],
                   item["prices"]["wasPrice"]["value"], link,
                   item["packageSize"], date.today().strftime("%Y-%m-%d"),
                   expiry_date)

            processed_data.append(tup)

        return processed_data

    def _get_items(self):
        items = []
        result_length = 1

        json_args = {
            "pagination": {
                "from": 0,
                "size": 48
            },
            "banner": "loblaw",
            "cartId": "3f42eeee-5594-42e0-8866-f9328958d735",
            "lang": "en",
            "date": datetime.today().strftime("%d%m%Y"),
            "storeId": "1000",
            "pcId": None,
            "pickupType": "STORE",
            "offerType": "ALL",
            "filter": {
                "categories": [
                    "27985"
                ],
                "promotions": [
                    "Price Reduction"
                ]
            }
        }

        headers = {"x-api-key", self.X_API_KEY}
        while result_length != 0:
            deals_response = requests.post(headers=headers, json=json_args)

            if deals_response.status_code != 200:
                return []

            products = deals_response.json()["results"]
            items.append(products)
            json_args["pagination"]["from"] += 1
            result_length = len(products)

        return items
