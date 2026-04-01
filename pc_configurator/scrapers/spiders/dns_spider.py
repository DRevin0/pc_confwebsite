import scrapy
import pickle
import json
import re
from pathlib import Path
from urllib.parse import urljoin
from scrapy_playwright.page import PageMethod
from ..utils.category import category_config

class DnsSpider(scrapy.Spider):
    name = 'dns_spider'
    allowed_domains = ['dns-shop.ru']

    DEFAULT_START_URL = "https://www.dns-shop.ru/catalog/88f4ff1d39dee00e/osnovnye-komplektuusie-dla-pk/"

    REQUIRED_CATEGORIES_KEYS = category_config.REQUIRED_CATEGORIES_KEYS_dns
    CATEGORY_KEYWORDS = category_config.CATEGORY_KEYWORDS_dns
    FALLBACK_CATEGORY_MAP = category_config.FALLBACK_CATEGORY_MAP_dns
    CATEGORY_DB_MAP = category_config.CATEGORY_DB_MAP_dns

    ITEMS_PER_CATEGORY = 3

    def __init__(self, categories_json=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.categories = None
        if categories_json:
            try:
                self.categories = json.loads(categories_json)
            except json.JSONDecodeError as e:
                raise ValueError(f"categories_json не является валидным JSON: {e}")

        self._seen_product_urls = set()
        self.category_counts = {cat: 0 for cat in self.REQUIRED_CATEGORIES_KEYS}
        self.storage_state = None

        cookies_path = Path(__file__).parent.parent / "cookies" / "dns_cookies.pkl"
        try:
            with open(cookies_path, 'rb') as f:
                cookies_list = pickle.load(f)

            self.storage_state = {
                "cookies": [
                    {
                        "name": c['name'],
                        "value": c['value'],
                        "domain": c.get('domain', '.dns-shop.ru'),
                        "path": c.get('path', '/'),
                        "expires": c.get('expires', -1),
                        "httpOnly": c.get('httpOnly', False),
                        "secure": c.get('secure', True),
                        "sameSite": c.get('sameSite', 'Lax'),
                    }
                    for c in cookies_list
                ]
            }
            self.logger.info(f"Загружено {len(self.storage_state['cookies'])} кук из dns_cookies.pkl")
        except FileNotFoundError:
            self.logger.error("Файл dns_cookies.pkl не найден. Сначала запусти get_dns_cookies.py")
            self.storage_state = None

    def clean(self, text):
        return (text or "").strip()

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

    def init_categories(self, response):
        self.categories = self.extract_category_urls(response)
        if not self.categories:
            self.logger.error("Не удалось извлечь категории с агрегаторной страницы. Нужны categories_json.")
            return

        for key in self.REQUIRED_CATEGORIES_KEYS:
            if key not in self.categories:
                for fb_key in self.FALLBACK_CATEGORY_MAP.get(key, []):
                    if fb_key in self.categories:
                        self.categories[key] = self.categories[fb_key]
                        break

        missing = [k for k in self.REQUIRED_CATEGORIES_KEYS if k not in self.categories]
        if missing:
            self.logger.warning(f"Не найдены некоторые категории: {missing}. Они будут пропущены.")

        self.category_counts = {cat: 0 for cat in self.categories if cat in self.REQUIRED_CATEGORIES_KEYS}

        for cat_key, url in self.categories.items():
            if cat_key not in self.REQUIRED_CATEGORIES_KEYS:
                continue
            if not url:
                continue

            db_category = self.CATEGORY_DB_MAP.get(cat_key, cat_key)
            yield scrapy.Request(
                url,
                callback=self.parse_category,
                meta={
                    'category_key': cat_key,
                    'category': db_category,
                    "playwright": True,
                    "playwright_context_kwargs": {"storage_state": self.storage_state},
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.catalog-product", timeout=30000),
                    ],
                }
            )

    def start_requests(self):
        if not self.storage_state:
            self.logger.error("Файлы cookie не найдены, завершение работы")
            return

        if self.categories:
            for cat_key, url in self.categories.items():
                if not url:
                    continue
                db_category = self.CATEGORY_DB_MAP.get(cat_key, cat_key)
                yield scrapy.Request(
                    url,
                    callback=self.parse_category,
                    meta={
                        'category_key': cat_key,
                        'category': db_category,
                        "playwright": True,
                        "playwright_context_kwargs": {"storage_state": self.storage_state},
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", "div.catalog-product", timeout=30000),
                        ],
                    }
                )
        else:
            yield scrapy.Request(
                self.DEFAULT_START_URL,
                callback=self.init_categories,
                meta={
                    "playwright": True,
                    "playwright_context_kwargs": {"storage_state": self.storage_state},
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "body", timeout=10000),
                        PageMethod("wait_for_timeout", 3000),
                        PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                        PageMethod("wait_for_timeout", 2000),
                    ],
                },
            )

    def parse_category(self, response):
        category_key = response.meta.get('category_key')
        db_category = response.meta.get('category')
        if not category_key:
            return

        current = self.category_counts.get(category_key, 0)
        if current >= self.ITEMS_PER_CATEGORY:
            return

        product_links = self.extract_product_links(response)
        if not product_links:
            self.logger.warning(f"Не найдено ссылок на товары на странице: {response.url}")
            return

        requests_sent = 0
        for product_url in product_links:
            if current + requests_sent >= self.ITEMS_PER_CATEGORY:
                break
            if product_url in self._seen_product_urls:
                continue

            self._seen_product_urls.add(product_url)
            requests_sent += 1
            yield scrapy.Request(
                product_url,
                callback=self.parse_product,
                meta={
                    'category_key': category_key,
                    'category': db_category,
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                        PageMethod("wait_for_timeout", 2000),
                    ]
                }
            )

    def parse_product(self, response):
        category_key = response.meta.get('category_key')
        db_category = response.meta.get('category')

        if self.category_counts.get(category_key, 0) >= self.ITEMS_PER_CATEGORY:
            return

        name = response.css('h1.product-card-top__title::text').get()
        if not name:
            name = response.css('h1::text').get()
        name = self.clean(name)

        price = response.css('div.product-buy__price::text').get()
        if price:
            price = price.replace('\xa0', ' ').strip()
        else:
            price = response.css('div.product-buy_price-wrap span::text').get()
        if price:
            price = self.clean(price)

        specs = {}
        titles = response.css('div.product-card-top__specs-item-title::text').getall()
        values = response.css('div.product-card-top__specs-item-content::text').getall()
        if titles and values:
            for title, value in zip(titles, values):
                if title and value:
                    specs[self.clean(title).rstrip(':')] = self.clean(value)

        self.category_counts[category_key] += 1

        yield {
            'name': name,
            'price': price,
            'url': response.url,
            'category': db_category,
            **specs,
        }