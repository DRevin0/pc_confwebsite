import subprocess
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
ROOT_DIR = BASE_DIR.parent
COOKIES_PATH = BASE_DIR / "scrapers" / "cookies" / "yandex_market_cookies.pkl"

DEFAULT_START_URL = (
    "https://market.yandex.ru/catalog--komplektuiushchie-dlia-kompiutera-v-nizhnem-novgorode/26912630/list"
    "?rs=eJwzcvrEaM_BKLDwEKsEg8brNSYa04-zaswE4r87HrNrTAYypgDx1H-GGj1A-vVVbo3ZQLobiK_O_MCqcWPrM2YAcIobtw%2C%2C"
)

deps_dir = str(ROOT_DIR / ".python_deps")
browsers_dir = str(ROOT_DIR / ".playwright_browsers")
pythonpath = deps_dir + (os.environ.get("PYTHONPATH", "") and (":" + os.environ["PYTHONPATH"]) or "")

env = dict(os.environ)
env["PYTHONPATH"] = pythonpath
env["PLAYWRIGHT_BROWSERS_PATH"] = browsers_dir

if not COOKIES_PATH.exists():
    subprocess.run(
        [
            sys.executable,
            str(BASE_DIR / "scrapers" / "utils" / "cookie_fetchers" / "get_yandex_market_cookies.py"),
        ],
        check=True,
        env=env,
    )

subprocess.run(
    [
        "scrapy",
        "crawl",
        "yandex_market_spider",
        "-a",
        f"start_url={DEFAULT_START_URL}",
    ],
    cwd=BASE_DIR / "scrapers",
    check=True,
    env=env,
)

