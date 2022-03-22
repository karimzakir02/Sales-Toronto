from webapp.data_retriever_interface import DataRetrieverInterface
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver


class SeleniumWebscraper(DataRetrieverInterface):

    def __init__(self):
        # Each scraper will have its own webdriver to allow for easier
        # asynchronous scraping in the future
        options = Options()
        options.add_argument("no-sandbox")
        options.add_argument("disable-dev-shm-usage")
        options.add_argument("headless")
        options.add_argument("window-size=1400,2000")
        options.add_argument("log-level=2")
        self.driver = webdriver.Chrome(options=options)
