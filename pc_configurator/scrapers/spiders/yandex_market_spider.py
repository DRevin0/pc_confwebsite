import re
from urllib.parse import urljoin
from scrapy_playwright.page import PageMethod
from ..utils.category import category_config
from .base_spider import BaseSpider

class YandexMarketSpider(BaseSpider):
    name = "yandex_market_spider"
    allowed_domains = ["market.yandex.ru"]

    cookies_filename = "yandex_market_cookies.pkl"
    start_url = (
        "https://market.yandex.ru/catalog--komplektuiushchie-dlia-kompiutera-v-nizhnem-novgorode/26912630/list"
        "?rs=eJwzcvrEaM_BKLDwEKsEg8brNSYa04-zaswE4r87HrNrTAYypgDx1H-GGj1A-vVVbo3ZQLobiK_O_MCqcWPrM2YAcIobtw%2C%2C"
    )

    REQUIRED_CATEGORIES_KEYS = category_config.REQUIRED_CATEGORIES_KEYS_yandex
    CATEGORY_KEYWORDS = category_config.CATEGORY_KEYWORDS_yandex
    FALLBACK_CATEGORY_MAP = category_config.FALLBACK_CATEGORY_MAP_yandex
    CATEGORY_DB_MAP = category_config.CATEGORY_DB_MAP_yandex
    ITEMS_PER_CATEGORY = 40

    def __init__(self, start_url=None, categories_json=None, *args, **kwargs):
        super().__init__(categories_json=categories_json, *args, **kwargs)
        if start_url:
            self.start_url = start_url

    def extract_product_links(self, response):
        links = response.xpath("//a[contains(@href, '/card/')]/@href").getall()
        links = [urljoin(response.url, href) for href in links if href]

        if not links:
            links = re.findall(r"https?://market\.yandex\.ru/card/[^\"'\s>]+", response.text)

        result = []
        seen = set()
        for href in links:
            href = href.strip()
            if href and href not in seen and "/card/" in href:
                seen.add(href)
                result.append(href)
        return result

    def extract_category_urls(self, response):
        found = {}
        for a in response.xpath("//a[@href]"):
            href = a.xpath("@href").get()
            if not href:
                continue
            if "/card/" in href:
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

    def get_start_meta(self):
        return {
            "playwright": True,
            "playwright_context_kwargs": {"storage_state": self.storage_state},
            "playwright_page_methods": [
                PageMethod("wait_for_timeout", 3000),
            ],
        }

    def get_category_meta(self, category_key, db_category):
        return {
            'category_key': category_key,
            'category': db_category,
            "playwright": True,
            "playwright_context_kwargs": {"storage_state": self.storage_state},
            "playwright_page_methods": [
                PageMethod("wait_for_selector", "body", timeout=10000),
                PageMethod("wait_for_timeout", 3000),
                PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                PageMethod("wait_for_timeout", 2000),
            ],
        }

    def get_product_meta(self, category_key, db_category):
        return {
            'category_key': category_key,
            'category': db_category,
            "playwright": True,
            "playwright_page_methods": [
                PageMethod("wait_for_selector", "body", timeout=10000),
                PageMethod("wait_for_timeout", 2500),
            ],
        }

    def _extract_price(self, response):
        m = re.search(r'"price"\s*:\s*\{\s*"value"\s*:\s*"(\d+)"\s*,\s*"currency"\s*:\s*"RUR"', response.text)
        if m:
            return m.group(1)
        m2 = re.search(r'"price"\s*:\s*\{\s*"value"\s*:\s*"(\d+)"', response.text)
        if m2:
            return m2.group(1)
        return None

    def _extract_name(self, response):
        name = self.clean(response.xpath("//h1//text()").get())
        if not name:
            name = self.clean(response.xpath("//meta[@property='og:title']/@content").get())
        if not name:
            ld_title = response.xpath("//script[@type='application/ld+json']//text()").get()
            if ld_title:
                m = re.search(r'"title"\s*:\s*"([^"]{3,500})"', ld_title)
                if m:
                    name = self.clean(m.group(1))
        return name
    
    def _enrich_product_item(self, response, item):
        specs = {}
        spec_blocks = response.xpath('//div[contains(@class, "_3rW2x") and contains(@class, "_1o0tA")]')
        for block in spec_blocks:
            if block.xpath('.//a[@data-autotest-id="full-specs-link"]'):
                continue

            name = block.xpath('.//span[@data-auto="product-spec"]/text()').get()
            if not name:
                continue
            if name.lower() == 'артикул маркета':
                continue
            name = self.clean(name).rstrip(':')

            value = block.xpath('.//div[@class="b2ZT4"]//span/text()').get()
            if not value:
                value = block.xpath('.//div[@class="b2ZT4"]//div[contains(@class, "ds-text")]/text()').get()
            if not value:
                value = block.xpath('.//div[@class="b2ZT4"]/text()').get()
            if value:
                value = self.clean(value)
                specs[name] = value

        item.update(specs)
