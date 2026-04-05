import scrapy
import pickle
import json
from pathlib import Path
from scrapy_playwright.page import PageMethod
class BaseSpider(scrapy.Spider):
    cookies_filename = None
    start_url = None
    REQUIRED_CATEGORIES_KEYS = []
    CATEGORY_KEYWORDS = {}
    FALLBACK_CATEGORY_MAP = {}
    CATEGORY_DB_MAP = {}
    ITEMS_PER_CATEGORY = 0

    def __init__(self, categories_json=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categories = None
        if categories_json:
            try:
                self.categories = json.loads(categories_json)
            except json.JSONDecodeError as e:
                raise ValueError(f"categories_json не валидный JSON: {e}")

        self._seen_product_urls = set()
        self.category_counts = {}
        self.storage_state = None
        self._load_cookies()

    def _load_cookies(self):
        if not self.cookies_filename:
            self.logger.error("cookies_filename не задан")
            return
        cookies_path = Path(__file__).parent.parent / "cookies" / self.cookies_filename
        try:
            with open(cookies_path, 'rb') as f:
                cookies_list = pickle.load(f)
            self.storage_state = {
                "cookies": [
                    {
                        "name": c['name'],
                        "value": c['value'],
                        "domain": c.get('domain', '.dns-shop.ru'),  # уточнять в дочерних
                        "path": c.get('path', '/'),
                        "expires": c.get('expires', -1),
                        "httpOnly": c.get('httpOnly', False),
                        "secure": c.get('secure', True),
                        "sameSite": c.get('sameSite', 'Lax'),
                    }
                    for c in cookies_list
                ]
            }
            self.logger.info(f"Загружено {len(self.storage_state['cookies'])} кук из {self.cookies_filename}")
        except FileNotFoundError:
            self.logger.error(f"Файл {self.cookies_filename} не найден. Сначала запустите скрипт получения кук.")
            self.storage_state = None
    
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
                    meta=self.get_category_meta(cat_key, db_category)
                )
        else:
            yield scrapy.Request(
                self.start_url,
                callback=self.init_categories,
                meta=self.get_start_meta()
            )
    
    def init_categories(self, response):
        self.categories = self.extract_category_urls(response)
        if not self.categories:
            self.logger.error("Не удалось извлечь категории. Нужен categories_json.")
            return

        # Fallback для недостающих категорий
        for key in self.REQUIRED_CATEGORIES_KEYS:
            if key not in self.categories:
                for fb_key in self.FALLBACK_CATEGORY_MAP.get(key, []):
                    if fb_key in self.categories:
                        self.categories[key] = self.categories[fb_key]
                        break

        missing = [k for k in self.REQUIRED_CATEGORIES_KEYS if k not in self.categories]
        if missing:
            self.logger.warning(f"Не найдены категории: {missing}")

        self.category_counts = {cat: 0 for cat in self.categories if cat in self.REQUIRED_CATEGORIES_KEYS}

        for cat_key, url in self.categories.items():
            if cat_key not in self.REQUIRED_CATEGORIES_KEYS or not url:
                continue
            db_category = self.CATEGORY_DB_MAP.get(cat_key, cat_key)
            yield scrapy.Request(
                url,
                callback=self.parse_category,
                meta=self.get_category_meta(cat_key, db_category)
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
            self.logger.warning(f"Нет ссылок на товары на {response.url}")
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
                meta=self.get_product_meta(category_key, db_category)
            )

    def parse_product(self, response):
        category_key = response.meta.get('category_key')
        db_category = response.meta.get('category')

        if self.category_counts.get(category_key, 0) >= self.ITEMS_PER_CATEGORY:
            return

        name = self.clean(response.xpath("//h1//text()").get())
        price = self._extract_price(response)

        item = {
            'name': name,
            'price': price,
            'url': response.url,
            'category': db_category,
        }

        self._enrich_product_item(response, item)

        self.category_counts[category_key] = self.category_counts.get(category_key, 0) + 1

        yield item

    def _enrich_product_item(self, response, item):
        pass

    def _extract_price(self, response):
        return None

    def extract_product_links(self, response):
        raise NotImplementedError

    def extract_category_urls(self, response):
        raise NotImplementedError
    
    def _extract_name(self, response):
        return self.clean(response.xpath("//h1//text()").get())

    def get_start_meta(self):
        return {
            "playwright": True,
            "playwright_context_kwargs": {"storage_state": self.storage_state},
            "playwright_page_methods": [
                PageMethod("wait_for_selector", "body", timeout=10000),
                PageMethod("wait_for_timeout", 3000),
                PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                PageMethod("wait_for_timeout", 2000),
            ],
        }

    def get_category_meta(self, category_key, db_category):
        """Мета для запроса страницы категории."""
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
        """Мета для запроса карточки товара."""
        return {
            'category_key': category_key,
            'category': db_category,
            "playwright": True,
            "playwright_page_methods": [
                PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                PageMethod("wait_for_timeout", 2000),
            ]
        }
    
    @staticmethod
    def clean(text):
        return (text or "").strip()
    

