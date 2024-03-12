# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RentfasterItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    WebLink = scrapy.Field()
    ListingID = scrapy.Field()
    Type = scrapy.Field()
    Price = scrapy.Field()
    Address = scrapy.Field()
    Number = scrapy.Field()
    pass
