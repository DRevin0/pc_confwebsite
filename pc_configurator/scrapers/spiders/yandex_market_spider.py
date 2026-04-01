import json
import pickle
import re
from pathlib import Path
from urllib.parse import urljoin
import scrapy
from scrapy_playwright.page import PageMethod
from ..utils.category import category_config

class YandexMarketSpider(scrapy.Spider):
    name = "yandex_market_spider"
    allowed_domains = ["market.yandex.ru"]

    DEFAULT_START_URL = (
        "https://market.yandex.ru/catalog--komplektuiushchie-dlia-kompiutera-v-nizhnem-novgorode/26912630/list"
        "?rs=eJwzcvrEaM_BKLDwEKsEg8brNSYa04-zaswE4r87HrNrTAYypgDx1H-GGj1A-vVVbo3ZQLobiK_O_MCqcWPrM2YAcIobtw%2C%2C"
    )

    REQUIRED_CATEGORIES_KEYS = category_config.REQUIRED_CATEGORIES_KEYS_yandex
    CATEGORY_KEYWORDS = category_config.CATEGORY_KEYWORDS_yandex
    FALLBACK_CATEGORY_MAP = category_config.FALLBACK_CATEGORY_MAP_yandex
    CATEGORY_DB_MAP = category_config.CATEGORY_DB_MAP_yandex

    ITEMS_PER_CATEGORY = 1

    def __init__(self, start_url=None, categories_json=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_url = start_url or self.DEFAULT_START_URL

        self.categories = None
        if categories_json:
            try:
                self.categories = json.loads(categories_json)
            except json.JSONDecodeError as e:
                raise ValueError(f"categories_json не является валидным JSON: {e}")

        self._seen_product_urls = set()
        self.category_counts = {cat: 0 for cat in self.REQUIRED_CATEGORIES_KEYS}
        self.storage_state = None

        cookies_path = Path(__file__).parent.parent / "cookies" / "yandex_market_cookies.pkl"
        try:
            with open(cookies_path, "rb") as f:
                cookies_list = pickle.load(f) or []

            self.storage_state = {
                "cookies": [
                    {
                        "name": c.get("name"),
                        "value": c.get("value"),
                        "domain": c.get("domain", ".market.yandex.ru"),
                        "path": c.get("path", "/"),
                        "expires": c.get("expires", -1),
                        "httpOnly": c.get("httpOnly", False),
                        "secure": c.get("secure", True),
                        "sameSite": c.get("sameSite", "Lax"),
                    }
                    for c in cookies_list
                    if c.get("name") is not None and c.get("value") is not None
                ]
            }
            self.logger.info(f"Загружено {len(self.storage_state['cookies'])} кук из yandex_market_cookies.pkl")
        except FileNotFoundError:
            self.logger.error(
                "Файл cookie yandex_market_cookies.pkl не найден. "
                "Сначала запустите get_yandex_market_cookies.py"
            )
            self.storage_state = None

    def start_requests(self):
        if not self.storage_state:
            self.logger.error("Файлы cookie не найдены, завершение работы")
            return

        if not self.categories:
            yield scrapy.Request(
                self.start_url,
                callback=self.init_categories,
                meta={
                    "playwright": True,
                    "category": None,
                    "playwright_context_kwargs": {
                        "storage_state": self.storage_state,
                    },
                    "playwright_page_methods": [
                        PageMethod("wait_for_timeout", 3000),
                    ],
                },
            )
            return

        for cat, url in self.categories.items():
            if not url:
                continue

            db_category = self.CATEGORY_DB_MAP.get(cat, cat)
            yield scrapy.Request(
                url,
                callback=self.parse_category,
                meta={
                    "category_key": cat,
                    "category": db_category,
                    "playwright": True,
                    "playwright_context_kwargs": {
                        "storage_state": self.storage_state,
                    },
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "body", timeout=10000),
                        PageMethod("wait_for_timeout", 3000),
                        PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                        PageMethod("wait_for_timeout", 2000),
                    ],
                },
            )

    def clean(self, text):
        return (text or "").strip()

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

        for cat, url in self.categories.items():
            if cat not in self.REQUIRED_CATEGORIES_KEYS:
                continue
            if not url:
                continue

            db_category = self.CATEGORY_DB_MAP.get(cat, cat)
            yield scrapy.Request(
                url,
                callback=self.parse_category,
                meta={
                    "category_key": cat,
                    "category": db_category,
                    "playwright": True,
                    "playwright_context_kwargs": {
                        "storage_state": self.storage_state,
                    },
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "body", timeout=10000),
                        PageMethod("wait_for_timeout", 3000),
                        PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                        PageMethod("wait_for_timeout", 2000),
                    ],
                },
            )

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

    def parse_category(self, response):
        category_key = response.meta.get("category_key")
        db_category = response.meta.get("category")
        if not category_key:
            return

        current = self.category_counts.get(category_key, 0)
        if current >= self.ITEMS_PER_CATEGORY:
            return

        product_links = self.extract_product_links(response)
        if not product_links:
            self.logger.warning(f"Не нашёл ссылок на карточки на странице: {response.url}")
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
                    "category_key": category_key,
                    "category": db_category,
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "body", timeout=10000),
                        PageMethod("wait_for_timeout", 2500),
                    ],
                },
            )

    def parse_product(self, response):
        db_category = response.meta.get("category")
        category_key = response.meta.get("category_key")

        name = self.clean(response.xpath("//h1//text()").get())
        if not name:
            name = self.clean(response.xpath("//meta[@property='og:title']/@content").get())
        if not name:
            ld_title = response.xpath("//script[@type='application/ld+json']//text()").get()
            if ld_title:
                m = re.search(r'"title"\s*:\s*"([^"]{3,500})"', ld_title)
                if m:
                    name = self.clean(m.group(1))

        price_digits = None
        m = re.search(r'"price"\s*:\s*\{\s*"value"\s*:\s*"(\d+)"\s*,\s*"currency"\s*:\s*"RUR"', response.text)
        if m:
            price_digits = m.group(1)
        else:
            m2 = re.search(r'"price"\s*:\s*\{\s*"value"\s*:\s*"(\d+)"', response.text)
            if m2:
                price_digits = m2.group(1)

        if category_key:
            self.category_counts[category_key] = self.category_counts.get(category_key, 0) + 1

        yield {
            "name": name,
            "price": price_digits,
            "url": response.url,
            "category": db_category or "",
        }

