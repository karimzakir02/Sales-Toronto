from interfaces import BuilderInterface
from .freshco_selenium_webscraper import FreshcoSeleniumWebscraper
from .metro_selenium_webscraper import MetroSeleniumWebscraper
from .loblaws_selenium_webscraper import LoblawsSeleniumWebscraper


class Builder(BuilderInterface):

    def build_retrievers():
        scrapers_list = []

        scrapers_list.append(FreshcoSeleniumWebscraper())
        scrapers_list.append(MetroSeleniumWebscraper())
        scrapers_list.append(LoblawsSeleniumWebscraper())

        return scrapers_list
