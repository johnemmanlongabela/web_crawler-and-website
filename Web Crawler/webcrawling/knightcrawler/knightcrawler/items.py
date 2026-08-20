# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class KnightcrawlerItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    source = scrapy.Field()
    date = scrapy.Field()
    summary = scrapy.Field()

