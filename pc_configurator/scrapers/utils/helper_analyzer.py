#scrapers/helper_analyzer
def build_technical_city_url(gpu_name: str) -> str:
    slug = gpu_name.replace(" ", "-")
    return f"https://technical.city/ru/video/{slug}"