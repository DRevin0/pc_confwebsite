from analyzer.models import GPUFPS
import subprocess


def get_fps_for_gpu(gpu_name: str):
    qs = GPUFPS.objects.filter(gpu_name=gpu_name)
    if qs.exists():
        return qs

    subprocess.run(
        ["scrapy", "crawl", "gpu_spider", "-a", f"gpu_name={gpu_name}"], cwd="scrapers"
    )

    return GPUFPS.objects.filter(gpu_name=gpu_name)
