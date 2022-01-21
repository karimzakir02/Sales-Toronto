from . import scrapers


def build_scrapers():
    scrapers_list = []

    scrapers_list.append(scrapers.LoblawsScraper())
    scrapers_list.append(scrapers.MetroScraper())

    return scrapers_list
