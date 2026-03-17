import scrapy
import pickle
from pathlib import Path
from scrapy_playwright.page import PageMethod


class DnsSpider(scrapy.Spider):
    name = 'dns_spider'
    allowed_domains = ['dns-shop.ru']

    categories = {
        'cpu': 'https://www.dns-shop.ru/catalog/17a899cd16404e77/processory/',
        'motherboard':'https://www.dns-shop.ru/catalog/17a89a0416404e77/materinskie-platy/',
        'gpu':'https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/',
        'ssd_sata':'https://www.dns-shop.ru/catalog/8a9ddfba20724e77/ssd-nakopiteli/',
        'ssd_m2':'https://www.dns-shop.ru/catalog/dd58148920724e77/ssd-m2-nakopiteli/',
        'ram':'https://www.dns-shop.ru/catalog/17a89a3916404e77/operativnaa-pamat-dimm/',
        'psu':'https://www.dns-shop.ru/catalog/17a89c2216404e77/bloki-pitania/',
        'air_cooling':'https://www.dns-shop.ru/catalog/17a9cc2d16404e77/kulery-dla-processorov/',
        'liquid_cooling':'https://www.dns-shop.ru/catalog/17a9cc9816404e77/sistemy-zidkostnogo-ohlazdenia/',
        'case':'https://www.dns-shop.ru/catalog/17a89c5616404e77/korpusa/',
    }
    start_urls = list(categories.values())
    MAX_PAGES = 1
    ITEMS_PER_CATEGORY = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category_counts = {cat: 0 for cat in self.categories}

        cookies_path = Path(__file__).parent.parent / "cookies" / "dns_cookies.pkl"
        try:
            with open(cookies_path, 'rb') as f:
                cookies_list = pickle.load(f)
            
            #Преобразование кук в формат для Playwright
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

    def start_requests(self):
        if not self.storage_state:
            self.logger.error("Файлы cookie не найдены, завершение работы")
            return

        for cat, url in self.categories.items():
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={
                    'category':cat,
                    "playwright": True,
                    "playwright_context_kwargs": {
                        "storage_state": self.storage_state,  
                    },
                    "playwright_page_methods": [
                        #PageMethod("wait_for_selector", "body", timeout=30000),
                        PageMethod("wait_for_selector", "div.catalog-product", timeout=30000),
                    ],
                }
            )

    def parse(self, response):
        #self.logger.info(f"parse вызван для {response.url}")
        #self.logger.info(f"Статус ответа: {response.status}")
        category = response.meta['category']
        current = self.category_counts[category]
        if current >= self.ITEMS_PER_CATEGORY:
            return
        
        products = response.css('div.catalog-product')
        self.logger.info(f"Найдено товаров: {len(products)}")
        requests_sent = 0

#        page_number = response.meta.get('page', 1)

        for product in products:
            if current + requests_sent >= self.ITEMS_PER_CATEGORY:
                self.logger.info(f"{category}, лимит товаров достигнут, останавливаем отправку новых запросов")
                break
            product_url = product.css('a.catalog-product__name::attr(href)').get()
            #self.logger.info(f"Найдена ссылка: {product_url}")
            if product_url:
                yield response.follow(
                    product_url,
                    callback=self.parse_product,
                    meta={
                        'category':category,
                        'playwright': True,
                        'playwright_page_methods': [
                            #PageMethod("wait_for_selector", "div.product-card-top_specs-item-title", timeout=30000),
                            PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                            PageMethod("wait_for_timeout", 2000),
                        ]
                    }
                )
                requests_sent += 1

        # Пагинация(на днс не используется)
#        if self.items_scraped + requests_sent < self.MAX_ITEMS: #page_number < self.MAX_PAGES
#            next_page = response.css('a.pagination-widget__page-link_next::attr(href)').get()
#            if next_page:
#                yield response.follow(
#                    next_page,
#                    callback=self.parse,
#                    meta={
#                        'playwright': True,
#                        'playwright_page_methods': [
#                            #PageMethod("add_cookies", self.playwright_cookies),  # на всякий случай
#                            PageMethod("wait_for_selector", "div.catalog-item"),
#                        ],
#                        'page': page_number + 1
#                    }
#                )

    def parse_product(self, response):
        category = response.meta['category']
        if self.category_counts[category] >= self.ITEMS_PER_CATEGORY:
            self.logger.debug(f"{category}, лимит товаров достигнут, останавливаем отправку новых запросов")
            return
        name = response.css('h1.product-card-top__title::text').get()
        if not name:
            name = response.css('h1::text').get()
        self.logger.info(f"Название: {name}")

        price = response.css('div.product-buy__price::text').get()
        if price:
            price = price.replace('\xa0', ' ').strip()
        else:
            price = response.css('div.product-buy_price-wrap span::text').get()
        self.logger.info(f"Цена: {price}")

        specs = {}

        titles2 = response.css('div.product-card-top__specs-item-title::text').getall()
        values2 = response.css('div.product-card-top__specs-item-content::text').getall()
        if titles2 and values2:
            for title, value in zip(titles2, values2):
                if title and value:
                    specs[title.strip().rstrip(':')] = value.strip()
            self.logger.info(f"Найдено характеристик: {len(specs)}")
        self.logger.debug(f"Характеристики: {specs}")

        self.category_counts[category] += 1
        yield {
            'name': name,
            'price': price,
            **specs,
        }
        if self.category_counts[category] >= self.ITEMS_PER_CATEGORY:
            self.logger.debug(f"{category}, лимит товаров достигнут, останавливаем отправку новых запросов")