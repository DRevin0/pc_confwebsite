import scrapy 


class BaseSpider(scrapy.Spider):
    name = 'base_spider'
    allowed_domains = ['parsemachine.com']
    start_urls = ['https://parsemachine.com/sandbox/catalog/']

    MAX_PAGES = 4

    def clean(self, text):
        return (text or "").strip()
    
    def parse(self, response):
        page_number = response.meta.get('page', 1)
        products = response.xpath("//div[@class='card-body']")
        for product in products:
            yield{
                'title':self.clean(product.xpath(".//h6[@class='card-title']/a[@class='no-hover title']/text()").get()),
                'selector':self.clean(product.xpath(".//p[@class='mb-1']/samp[@class='selector']/text()").get()),
                'link': response.urljoin(product.xpath(".//h6[@class='card-title']/a/@href").get()),
            }
        if page_number < self.MAX_PAGES:
            next_page = response.xpath("//a[contains(., 'Следующая')]/@href").get()
            if next_page:
                yield response.follow(
                    next_page, 
                    callback=self.parse, 
                    meta={'page': page_number + 1}
                )
