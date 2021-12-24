from . import scrapers


def build_scrapers():
    scrapers_list = []

    scrapers_list.append(scrapers.LoblawsScraper())

    return scrapers_list
