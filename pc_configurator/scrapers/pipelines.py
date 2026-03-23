# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import re
from decimal import Decimal
from asgiref.sync import sync_to_async
from components.models import Component, Price, Spec

class DjangoPipeline:
    async def process_item(self, item, spider):
        # Обрабатываем только нужные пауки
        if spider.name not in ['citilink_spider', 'dns_spider']:
            return item

        url = item.get('url')
        if not url:
            spider.logger.warning(f"Item без URL, пропускаем: {item}")
            return item

        # Создаём или получаем компонент
        component, created = await sync_to_async(Component.objects.get_or_create)(
            url=url,
            defaults={
                'name': item.get('name', ''),
                'category': item.get('category', ''),
            }
        )

        if not created and component.name != item.get('name'):
            component.name = item.get('name')
            await sync_to_async(component.save)()

        # Сохраняем цену
        price_str = item.get('price')
        if price_str:
            price_clean = re.sub(r'[^\d]', '', price_str)
            if price_clean:
                try:
                    await sync_to_async(Price.objects.create)(
                        component=component,
                        price=Decimal(price_clean)
                    )
                except Exception as e:
                    spider.logger.error(f"Ошибка цены '{price_str}': {e}")

        # Сохраняем характеристики
        exclude = {'name', 'price', 'category', 'url'}
        for key, value in item.items():
            if key not in exclude and value:
                await sync_to_async(Spec.objects.update_or_create)(
                    component=component,
                    key=key,
                    defaults={'value': value.strip() if isinstance(value, str) else value}
                )

        spider.logger.debug(f"Сохранён: {component.name}")
        return item