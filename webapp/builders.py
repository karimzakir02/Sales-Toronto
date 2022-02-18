from abc import ABC, abstractmethod
from . import webscrapers


class RetrieverBuilder(ABC):

    @abstractmethod
    def build_retrievers():
        raise NotImplementedError


class WebScraperBuilder(RetrieverBuilder):

    def build_retrievers():
        scrapers_list = []

        scrapers_list.append(webscrapers.FreshcoScraper())
        scrapers_list.append(webscrapers.LoblawsScraper())
        scrapers_list.append(webscrapers.MetroScraper())

        return scrapers_list
