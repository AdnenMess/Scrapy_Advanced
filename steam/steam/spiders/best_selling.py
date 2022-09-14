import json

import scrapy
from w3lib.html import remove_tags
from ..items import SteamItem


def get_platforms(list_classes):
    platforms = []
    for item in list_classes:
        platform = item.split()[-1]
        if platform == 'win':
            platforms.append('Windows')
        elif platform == 'mac':
            platforms.append('Mac os')
        elif platform == 'linux':
            platforms.append('Linux')
        elif platform == 'vr_supported':
            platforms.append('VR Supported')
    return platforms


def remove_html(review_summary):
    cleaned_review_summary = ''
    try:
        cleaned_review_summary = remove_tags(review_summary)
    except TypeError:
        cleaned_review_summary = 'No reviews'
    return cleaned_review_summary


def clean_discount_rate(discount_rate):
    if discount_rate:
        return discount_rate.lstrip('-')
    return discount_rate


def clean_discount_price(discount_price):
    if discount_price:
        return discount_price.strip()
    return discount_price


def get_original_price(selector_obj):
    original_price = ''
    div_with_discount = selector_obj.xpath(".//div[contains(@class, 'search_price discounted')]")
    if len(div_with_discount) > 0:
        original_price = div_with_discount.xpath(".//span/strike/text()").get()
    else:
        original_price = selector_obj.xpath("normalize-space(.//div[contains(@class, 'search_price')]/text())").get()
    return original_price


class BestSellingSpider(scrapy.Spider):
    name = 'best_selling'
    allowed_domains = ['store.steampowered.com']
    start_urls = [f'https://store.steampowered.com/search/?filter=topsellers&page=1']

    def parse(self, response, **kwargs):
        steam_item = SteamItem()
        games = response.xpath("//div[@id='search_resultsRows']/a")
        for game in games:
            steam_item['game_url'] = game.xpath(".//@href").get()
            steam_item['img_url'] = game.xpath(".//div[@class='col search_capsule']/img/@src").get()
            steam_item['game_name'] = game.xpath(".//span[@class='title']/text()").get()
            steam_item['release_date'] = game.xpath(".//div[contains(@class, 'col search_released')]/text()").get()
            steam_item['platforms'] = get_platforms(
                game.xpath(".//span[@class='vr_supported' or contains(@class, 'platform_img')]/@class").getall())
            steam_item['reviews_summary'] = remove_html(
                game.xpath(".//span[contains(@class, 'search_review_summary')]/@data-tooltip-html").get())
            steam_item['discount_rate'] = clean_discount_rate(
                game.xpath(".//div[contains(@class, 'search_discount')]/span/text()").get())
            steam_item['original_price'] = get_original_price(
                game.xpath(".//div[contains(@class, 'search_price_discount_combined')]"))
            steam_item['discount_price'] = clean_discount_price(
                game.xpath("(.//div[contains(@class, 'search_price discounted')]/text())[2]").get())

            yield steam_item

        next_page = response.xpath("//a[@class='pagebtn' and text()='>']/@href").get()

        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse)
