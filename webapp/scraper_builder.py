from . import webscrapers


def build_scrapers():
    scrapers_list = []

    scrapers_list.append(webscrapers.LoblawsScraper())
    scrapers_list.append(webscrapers.MetroScraper())

    return scrapers_list
