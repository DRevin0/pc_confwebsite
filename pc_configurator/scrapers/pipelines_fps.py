# scrapers/pipelines_fps.py
import os
import sys
import django
from asgiref.sync import sync_to_async

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from analyzer.models import GPUFPS


class SaveFPSPipeline:
    
    async def process_item(self, item, spider):
        if spider.name != "gpu_spider":
            return item

        gpu_name = item.get("gpu_name")
        game = item.get("game")
        resolution = item.get("resolution")
        fps_min = item.get("fps_min")
        fps_max = item.get("fps_max")

        print(f"SaveFPSPipeline получил item: {item}")

        if not all([gpu_name, game, resolution, fps_min is not None]):
            spider.logger.warning(f"FPS item пропущен из-за отсутствия данных: {item}")
            return item

        try:
            obj, created = await sync_to_async(GPUFPS.objects.update_or_create)(
                gpu_name=gpu_name,
                game=game,
                resolution=resolution,
                defaults={
                    "fps_min": fps_min,
                    "fps_max": fps_max,
                }
            )
            spider.logger.info(f"FPS сохранён: {gpu_name} | {game} | {resolution} | created={created}")
        except Exception as e:
            spider.logger.error(f"Ошибка сохранения FPS: {e}")
            import traceback
            traceback.print_exc()

        return item