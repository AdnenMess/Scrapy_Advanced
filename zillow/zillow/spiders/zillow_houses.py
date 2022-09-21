import scrapy
from scrapy.loader import ItemLoader
from ..utils import URL, cookie_parser, parse_new_url
from ..items import ZillowItem
import json


class ZillowHousesSpider(scrapy.Spider):
    name = 'zillow_houses'
    allowed_domains = ['www.zillow.com']

    def start_requests(self):
        yield scrapy.Request(url=URL, callback=self.parse, cookies=cookie_parser(),
                             meta={'currentPage': 1})

    def parse(self, response, **kwargs):
        current_page = response.meta['currentPage']
        json_resp = json.loads(response.body)
        houses = json_resp.get('cat1').get('searchResults').get('listResults')
        for house in houses:
            loader = ItemLoader(item=ZillowItem())
            loader.add_value('id', house.get('id'))
            loader.add_value('img_src', house.get('imgSrc'))
            loader.add_value('detail_url', house.get('detailUrl'))
            loader.add_value('status_type', house.get('statusType'))
            loader.add_value('status_text', house.get('statusText'))
            loader.add_value('price', house.get('price'))
            loader.add_value('address', house.get('address'))
            loader.add_value('beds', house.get('beds'))
            loader.add_value('baths', house.get('baths'))
            loader.add_value('area_sqft', house.get('area'))
            loader.add_value('latitude', house.get('latLong').get('latitude'))
            loader.add_value('longitude', house.get('latLong').get('longitude'))
            loader.add_value('broker_name', house.get('brokerName'))
            yield loader.load_item()

        total_pages = int(json_resp.get('cat1').get('searchList').get('totalPages'))
        if current_page <= total_pages:
            current_page += 1
            yield scrapy.Request(url=parse_new_url(URL, page_number=current_page),
                                 callback=self.parse, cookies=cookie_parser(),
                                 meta={'currentPage': current_page})
