import scrapy
import pickle
from pathlib import Path
from scrapy_playwright.page import PageMethod

class CitilinkSpider(scrapy.Spider):
    name = 'citilink_spider'
    allowed_domains =['citilink.ru']

    categories = {
        'cpu':'https://www.citilink.ru/catalog/processory/?ref=mainpage_popular',
        'motherboard':'https://www.citilink.ru/catalog/materinskie-platy/?ref=mainpage_popular',
        'gpu':'https://www.citilink.ru/catalog/videokarty/?ref=mainpage_popular',
        'ssd':'https://www.citilink.ru/catalog/ssd-nakopiteli/?ref=mainpage_popular',
        'ram':'https://www.citilink.ru/catalog/moduli-pamyati/?ref=mainpage_popular',
        'psu':'https://www.citilink.ru/catalog/bloki-pitaniya/?ref=mainpage_popular',
        'cooling':'https://www.citilink.ru/catalog/sistemy-ohlazhdeniya-processora/?ref=mainpage_popular',
        'case':'https://www.citilink.ru/catalog/korpusa/?ref=mainpage_popular',
    }
    start_urls = list(categories.values())
    MAX_PAGES = 1
    ITEMS_PER_CATEGORY = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category_counts = {cat: 0 for cat in self.categories}

        cookies_path = Path(__file__).parent.parent / "cookies" / "citilink_cookies.pkl"
        try:
            with open(cookies_path, 'rb') as f:
                cookies_list = pickle.load(f)
            
            #Преобразование кук в формат для Playwright
            self.storage_state = {
                "cookies": [
                    {
                        "name": c['name'],
                        "value": c['value'],
                        "domain": c.get('domain', '.citilink.ru'),
                        "path": c.get('path', '/'),
                        "expires": c.get('expires', -1),
                        "httpOnly": c.get('httpOnly', False),
                        "secure": c.get('secure', True),
                        "sameSite": c.get('sameSite', 'Lax'),
                    }
                    for c in cookies_list
                ]
            }
            self.logger.info(f"Загружено {len(self.storage_state['cookies'])} кук из citilink_cookies.pkl")
        except FileNotFoundError:
            self.logger.error("Файл citilink_cookies.pkl не найден. Сначала запусти get_citilink_cookies.py")
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
                    "playwright":True,
                    "playwright_context_kwargs":{
                        "storage_state":self.storage_state,
                    },
                    "playwright_page_methods":[
                        PageMethod("wait_for_selector", 'div[data-meta-name="SnippetProductVerticalLayout"]', timeout=30000),
                    ],
                }
            )
    
    def parse(self, response):
        category = response.meta['category']
        current = self.category_counts[category]
        if current >= self.ITEMS_PER_CATEGORY:
            return
        products = response.css('div[data-meta-name="SnippetProductVerticalLayout"]')
        self.logger.info(f"Найдено товаров: {len(products)}")
        requests_sent = 0
        for product in products:
            if current + requests_sent >= self.ITEMS_PER_CATEGORY:
                self.logger.info(f"{category}, лимит товаров достигнут, останавливаем отправку новых запросов")
                break
            product_url = product.css('a[data-meta-name="Snippet__title"]::attr(href)').get()
            if product_url:
                yield response.follow(
                    product_url,
                    callback=self.parse_product,
                    meta={
                        'category':category,
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"),
                            PageMethod("wait_for_timeout", 2000),
                        ]
                    }
                )
                requests_sent += 1
    
    def parse_product(self, response):
        category = response.meta['category']
        if self.category_counts[category] >= self.ITEMS_PER_CATEGORY:
            self.logger.debug(f"{category}, лимит товаров достигнут, останавливаем отправку новых запросов")
            return
        
        name = response.css('h1::text').get()
        if not name:
            name = response.css('[data-meta-name="ProductName"]::text').get()
        self.logger.info(f"Название: {name}")

        price = response.css('[data-meta-price]::attr(data-meta-price)').get()
        if not price:
            price_block = response.css('span[class*="Price"]:contains("₽")::text').get()
            if price_block:
                price = price_block.replace('\xa0', ' ').strip()
        self.logger.info(f"Цена: {price}")

        specs = {}

        spec_items = response.css('li[class*="ProductPropertiesItem"]')

        if spec_items:
            for item in spec_items:
                title=item.css('span[class*="ProductPropertiesName"] ::text').get()
                value=item.css('span[class*="ProductPropertiesValue"] ::text').get()
                if title and value:
                    specs[title.strip().rstrip(':')]=value.strip()
            self.logger.info(f"Найдено характеристик:{len(specs)}")

        self.logger.debug(f"Характеристики: {specs}")
        self.category_counts[category] += 1
        yield {
            'name': name,
            'price': price,
            'url':response.url,
            'category':category,
            **specs,
        }
        if self.category_counts[category] >= self.ITEMS_PER_CATEGORY:
            self.logger.debug(f"{category}, лимит товаров достигнут, останавливаем отправку новых запросов")