# Script to scrape loblaws.ca and their deals

from seleniumwire import webdriver
import time
from seleniumwire.utils import decode
import json

LOBLAWS_URL = "https://www.loblaws.ca/deals/all?sort=relevance&category=27985&promotions=Price%20Reduction"
POST_URL = "https://api.pcexpress.ca/product-facade/v3/products/deals"


options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument('window-size=1400,2000')
driver = webdriver.Chrome(options=options)
driver.get(LOBLAWS_URL)
time.sleep(5)

last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    time.sleep(1)

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

count = 0
driver.save_screenshot("loblaws_screenshot.png")
for request in driver.requests:
    if request.url == POST_URL:
        response = request.response
        count += 1
        body = decode(response.body, response.headers.get("Content-Encoding",
                                                          "identity"))
        json_body = json.loads(body.decode("utf-8"))
        print(f"{count}\n ")
        print(json_body["results"][0])
        print("\n")
        # for result in json_body["results"]:
        #     print(result["name"])
        # print(len(json_body["results"]))

driver.quit()
print(count)
# You can find all of the product titles easily, since they have a common
# class name
# Also, check if you can check any requests sent by the page using selenium
# Would make it much easier if you just could copy the JSON obtained by the
# page itself

# https://pypi.org/project/selenium-wire/#response-objects
# For easier processing, maybe use selenium-wire. I think it will allow you
# to check which requests a browser sent and what the responses were
# The important thing to remember though is that the deals are sent in batches
# of json objects, so it's a question of whether it will be easier to just
# work with the json objects. Chances are it probably is.
# Filter for the request using its URL (api.pcoptimum....)
