import re
import logging
import scrapy
from scrapers.utils.helper_analyzer import build_technical_city_url

logger = logging.getLogger(__name__)

class TechnicalCityGPU(scrapy.Spider):
    name = "technical_city_gpu"

    def __init__(self, gpu_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not gpu_name:
            raise ValueError("gpu_name parameter is required")
        self.gpu_name = gpu_name
        self.start_urls = [build_technical_city_url(gpu_name)]

    def parse(self, response):
        tab_labels = []
        for span in response.css("ul.tab-control_show_all_tab_titles li span"):
            raw = span.xpath("string(.)").get() or ""
            raw = raw.strip()
            if raw:
                tab_labels.append(raw)
        if not tab_labels:
            for sel in ("div.tabs-nav li span::text", "ul.tabs-list li::text"):
                labels = [l.strip() for l in response.css(sel).getall() if l.strip()]
                if labels:
                    tab_labels = labels
                    break

        tabs = response.css("div.tabs div.tab")
        for i, tab in enumerate(tabs):
            raw_label = tab_labels[i] if i < len(tab_labels) else (tab.xpath("string(.)").get() or "").strip()
            normalized = self._normalize_tab_label(raw_label) if raw_label else f"unknown-{i}"

            short_resolution = normalized.split("_", 1)[0] if "_" in normalized else normalized
            resolution_index = i

            for row in tab.css("table.compare-table tr"):
                game = row.css("td:nth-child(1)::text").get()
                if not game:
                    continue

                fps_raw = row.css("td:nth-child(2) span.td1 span::text").get()
                if not fps_raw:
                    fps_raw = row.css("td:nth-child(2)::text").get()
                if not fps_raw:
                    continue

                fps_min, fps_max = self.parse_fps(fps_raw)
                if fps_min is None:
                    continue

                yield {
                    "gpu_name": self.gpu_name,
                    "game": game.strip(),
                    "resolution": short_resolution, 
                    "fps_min": fps_min,
                    "fps_max": fps_max,
                }

    def _normalize_tab_label(self, raw: str) -> str:
        if not raw:
            return "unknown"
        t = re.sub(r'\s+', ' ', raw).strip().lower()
        t = t.replace("full hd", "fullhd")
        t = t.replace("4 k", "4k")
        t = t.replace(" ", "_").replace("/", "_")
        t = re.sub(r'[^a-z0-9_]+', '', t)
        return t or "unknown"

    @staticmethod
    def parse_fps(text):
        if not text:
            return None, None
        t = text.replace(" ", "").replace("FPS", "").strip()
        t = t.replace("–", "−").replace("-", "−")
        if "−" in t:
            parts = [p for p in t.split("−") if p]
            try:
                a = int(re.search(r'\d+', parts[0]).group())
                b = int(re.search(r'\d+', parts[1]).group()) if len(parts) > 1 else a
                return a, b
            except Exception:
                return None, None
        m = re.search(r'\d+', t)
        if m:
            v = int(m.group())
            return v, v
        return None, None


