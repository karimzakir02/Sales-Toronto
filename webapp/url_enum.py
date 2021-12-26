from strenum import StrEnum


class StoreURLs(StrEnum):
    LOBLAWS = ("https://www.loblaws.ca/deals/all?sort=relevance&"
               "category=27985&promotions=Price%20Reduction")
    METRO = ("https://www.metro.ca/en/flyer")
