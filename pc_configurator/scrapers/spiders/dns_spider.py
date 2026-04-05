import scrapy
import re
from urllib.parse import urljoin
from scrapy_playwright.page import PageMethod
from ..utils.category import category_config
from .base_spider import BaseSpider

class DnsSpider(BaseSpider):
    name = 'dns_spider'
    allowed_domains = ['dns-shop.ru']

    cookies_filename = 'dns_cookies.pkl'
    start_url = "https://www.dns-shop.ru/catalog/88f4ff1d39dee00e/osnovnye-komplektuusie-dla-pk/"

    REQUIRED_CATEGORIES_KEYS = category_config.REQUIRED_CATEGORIES_KEYS_dns
    CATEGORY_KEYWORDS = category_config.CATEGORY_KEYWORDS_dns
    FALLBACK_CATEGORY_MAP = category_config.FALLBACK_CATEGORY_MAP_dns
    CATEGORY_DB_MAP = category_config.CATEGORY_DB_MAP_dns
    ITEMS_PER_CATEGORY = 3

    def extract_product_links(self, response):
        links = response.css('a.catalog-product__name::attr(href)').getall()
        if not links:
            links = response.xpath('//a[contains(@href, "/product/")]/@href').getall()
        if not links:
            links = re.findall(r'https?://www\.dns-shop\.ru/product/[^"\'\\\s>]+', response.text)

        result = []
        seen = set()
        for href in links:
            href = href.strip()
            full_url = urljoin(response.url, href)
            if full_url not in seen:
                seen.add(full_url)
                result.append(full_url)
        return result

    def extract_category_urls(self, response):
        found = {}
        for a in response.xpath("//a[@href]"):
            href = a.xpath("@href").get()
            if not href:
                continue
            if "/product/" in href or "/card/" in href:
                continue
            if "catalog" not in href:
                continue

            text_parts = a.xpath(".//text()").getall()
            text = self.clean(" ".join(text_parts))
            if not text:
                continue

            text_lower = text.lower()
            for cat_key, keywords in self.CATEGORY_KEYWORDS.items():
                if cat_key in found:
                    continue
                for kw in keywords:
                    if kw.lower() in text_lower:
                        found[cat_key] = urljoin(response.url, href)
                        break
        return found

    def get_category_meta(self, category_key, db_category):
        return {
            'category_key': category_key,
            'category': db_category,
            "playwright": True,
            "playwright_context_kwargs": {"storage_state": self.storage_state},
            "playwright_page_methods": [
                PageMethod("wait_for_selector", "div.catalog-product", timeout=30000),
            ],
        }

    def get_product_meta(self, category_key, db_category):
        return {
            'category_key': category_key,
            'category': db_category,
            "playwright": True,
            "playwright_page_methods": [
                PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                PageMethod("wait_for_timeout", 2000),
            ]
        }

    def _extract_price(self, response):
        price = response.css('div.product-buy__price::text').get()
        if price:
            price = price.replace('\xa0', ' ').strip()
        else:
            price = response.css('div.product-buy_price-wrap span::text').get()
        if price:
            price = self.clean(price)
        return price

    def _enrich_product_item(self, response, item):
        specs = {}
        titles = response.css('div.product-card-top__specs-item-title::text').getall()
        values = response.css('div.product-card-top__specs-item-content::text').getall()
        if titles and values:
            for title, value in zip(titles, values):
                if title and value:
                    specs[self.clean(title).rstrip(':')] = self.clean(value)
        item.update(specs)