import json
from abc import ABC

import scrapy
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
from w3lib.http import basic_auth_header


class ListingsSpider(scrapy.Spider, ABC):
    name = 'listings'
    allowed_domains = ['www.centris.ca']

    position = {"startPosition": 0}

    script = """
            function main(splash, args)
              splash:on_request(function(request)
                if request.url:find('css') then
                    request.abort()
                end
              end)
              splash.js_enabled = false
              splash.images_enabled = false
              assert(splash:go(args.url))
              assert(splash:wait(0.5))
              return splash:html()
            end
    """

    def start_requests(self):
        # On the second page of search we have UpdateQuery, query is the Request Payload (view source)
        query = {
            "query": {
                "UseGeographyShapes": 0,
                "Filters": [
                    {
                        "MatchType": "GeographicArea",
                        "Text": "Montréal (Island)",
                        "Id": "GSGS4621"
                    },
                    {
                        "MatchType": "GeographicArea",
                        "Text": "Centre-du-Québec",
                        "Id": "RARA17"
                    }
                ],
                "FieldsValues": [
                    {
                        "fieldId": "GeographicArea",
                        "value": "GSGS4621",
                        "fieldConditionId": "",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "GeographicArea",
                        "value": "RARA17",
                        "fieldConditionId": "",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "Category",
                        "value": "Residential",
                        "fieldConditionId": "",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "SellingType",
                        "value": "Rent",
                        "fieldConditionId": "",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "LandArea",
                        "value": "SquareFeet",
                        "fieldConditionId": "IsLandArea",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "RentPrice",
                        "value": 0,
                        "fieldConditionId": "ForRent",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "RentPrice",
                        "value": 1500,
                        "fieldConditionId": "ForRent",
                        "valueConditionId": ""
                    }
                ]
            },
            "isHomePage": False
        }
        yield scrapy.Request(
            url="https://www.centris.ca/property/UpdateQuery", method="POST", body=json.dumps(query),
            headers={'Content-type': 'application/json'}, callback=self.update_query)

    def update_query(self, response):
        yield scrapy.Request(
            url="https://www.centris.ca/Property/GetInscriptions", method="POST", body=json.dumps(self.position),
            headers={'Content-type': 'application/json'}, callback=self.parse)

    def parse(self, response, **kwargs):
        resp_dict = json.loads(response.body)
        print(type(resp_dict))

        # to get the HTML response we go in GetInscriptions / Preview -> d: Result : html
        html = resp_dict.get('d').get('Result').get('html')
        # print(html)
        # with open('index.html', 'w') as f:
        #     f.write(html)

        sel = Selector(text=html)       # convert string to selector object so we can use xpath
        listings = sel.xpath("//div[contains(@class, 'property-thumbnail-item')]")
        for listing in listings:
            category = listing.xpath(
                "normalize-space(.//div[@class='location-container']/span[@class='category']/div/text())").get()
            address = listing.xpath(".//div[@class='location-container']/span[@class='address']/div[1]/text()").get()
            place = listing.xpath(".//div[@class='location-container']/span[@class='address']/div[2]/text()").get()
            currency = listing.xpath(".//div[@class='price']/meta[@itemprop='priceCurrency']/@content").get()
            price = listing.xpath(".//div[@class='price']/meta[@itemprop='price']/@content").get()
            url = response.urljoin(
                listing.xpath(".//div[contains(@class, 'legacy-reset')]/a[contains(@class,'property')]/@href").get())
            yield SplashRequest(
                url=url, endpoint='execute', callback=self.parse_summary, args={'lua_source': self.script},
                splash_headers={'Authorization': basic_auth_header('user', 'userpass')},
                meta={
                    'cat': category, 'add': address, 'pla': place, 'cur': currency, 'pri': price
                }
            )

        count = resp_dict.get("d").get("Result").get("count")
        increment_number = resp_dict.get("d").get("Result").get("inscNumberPerPage")

        if self.position["startPosition"] <= count:
            self.position["startPosition"] += increment_number
            yield scrapy.Request(
                url="https://www.centris.ca/Property/GetInscriptions", method="POST", callback=self.parse,
                body=json.dumps(self.position), headers={"Content-Type": "application/json"}
            )

    def parse_summary(self, response):
        address_full = response.xpath("//div[@class='col text-left pl-0']/h2/text()").get()
        description = response.xpath("normalize-space(//div[@itemprop='description']/text())").get()

        # Now get data (meta) from parse
        category = response.request.meta['cat']
        address = response.request.meta['add']
        place = response.request.meta['pla']
        currency = response.request.meta['cur']
        price = response.request.meta['pri']

        yield {
            'address': address, 'address_full': address_full, 'place': place, 'category': category,
            'description': description, 'currency': currency, 'price': price
        }
