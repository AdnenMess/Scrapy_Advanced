import json
from abc import ABC

import scrapy
from scrapy.selector import Selector


class ListingsSpider(scrapy.Spider, ABC):
    name = 'listings'
    allowed_domains = ['www.centris.ca']

    position = {"startPosition": 0}

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

    def remove_characters(self, value):
        return value.strip("\r\n ")

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
            category = listing.xpath(".//div[@class='location-container']/span[@class='category']/div/text()").get()
            address = listing.xpath(".//div[@class='location-container']/span[@class='address']/div[1]/text()").get()
            place = listing.xpath(".//div[@class='location-container']/span[@class='address']/div[2]/text()").get()
            currency = listing.xpath(".//div[@class='price']/meta[@itemprop='priceCurrency']/@content").get()
            price = listing.xpath(".//div[@class='price']/meta[@itemprop='price']/@content").get()
            url = response.urljoin(
                listing.xpath(".//div[contains(@class, 'legacy-reset')]/a[contains(@class,'property')]/@href").get())
            yield {
                'category': self.remove_characters(category),
                'address': address,
                'place': place,
                'currency': currency,
                'price': price,
                'url': url
            }

