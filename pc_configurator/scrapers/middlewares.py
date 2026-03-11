# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy import signals
from fake_useragent import UserAgent

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

"""
class RandomUserAgentMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        return cls()
    
    def __init__(self):
        self.ua = UserAgent()
    
    def process_request(self, request, spider):
        user_agent = self.ua.random
        request.headers['User-Agent'] = user_agent

        spider.logger.debug(f"🔄 UA: {user_agent[:70]}...")

        self._add_browser_headers(request, user_agent)

    def _add_browser_headers(self, request, ua):
        
        # Определяем браузер по строке UA
        if 'Firefox' in ua:
            accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            lang = 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
        elif 'Edg' in ua:
            accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            lang = 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
        elif 'Chrome' in ua:
            accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
            lang = 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
        elif 'Safari' in ua and 'Chrome' not in ua:
            accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            lang = 'ru-RU,ru;q=0.9,en;q=0.8'
        else:
            accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            lang = 'ru-RU,ru;q=0.9,en;q=0.8'
        
        # Устанавливаем заголовки ТОЛЬКО если их ещё нет
        request.headers.setdefault('Accept', accept)
        request.headers.setdefault('Accept-Language', lang)
        request.headers.setdefault('Accept-Encoding', 'gzip, deflate, br')
        request.headers.setdefault('Connection', 'keep-alive')
        request.headers.setdefault('Upgrade-Insecure-Requests', '1')
        
        # Sec-Fetch заголовки (для современных браузеров)
        if 'Chrome' in ua or 'Firefox' in ua or 'Edg' in ua:
            request.headers.setdefault('Sec-Fetch-Dest', 'document')
            request.headers.setdefault('Sec-Fetch-Mode', 'navigate')
            request.headers.setdefault('Sec-Fetch-Site', 'none')
            request.headers.setdefault('Sec-Fetch-User', '?1')
"""

class ScrapersSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    async def process_start(self, start):
        # Called with an async iterator over the spider start() method or the
        # matching method of an earlier spider middleware.
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ScrapersDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

