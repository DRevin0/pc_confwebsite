import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
subprocess.run(
    [
        sys.executable,
        str(BASE_DIR / "scrapers" / "utils" / "cookie_fetchers" / "get_dns_cookies.py"),
    ],
    check=True,
)

subprocess.run(["scrapy", "crawl", "dns_spider"], cwd=BASE_DIR / "scrapers", check=True)
