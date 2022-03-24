from interfaces import BuilderInterface
from loblaws_request_webscraper import LoblawsRequestWebscraper
from metro_request_webscraper import MetroRequestWebscraper


class Builder(BuilderInterface):

    def build_retrievers():
        scrapers_list = []

        scrapers_list.append(LoblawsRequestWebscraper())
        scrapers_list.append(MetroRequestWebscraper())

        return scrapers_list
