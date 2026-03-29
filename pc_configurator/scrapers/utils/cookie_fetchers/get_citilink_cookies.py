import pickle
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    cookies_dir = Path(__file__).parent.parent.parent / "cookies"
    cookies_dir.mkdir(exist_ok=True)
    cookies_path = cookies_dir / "citilink_cookies.pkl"

    url = (
        "https://www.citilink.ru/catalog/processory/?ref=mainpage_popular"
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled",
                  "--no-proxy-server"],
        )
        context = browser.new_context(
            locale="ru-RU",
            timezone_id="Europe/Moscow",
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        print(
            "Браузер открыт. Если появится капча/выбор адреса/вход — пройдите вручную.",
            flush=True,
        )
        print("После успешной загрузки нажмите Enter здесь...", flush=True)
        input()

        cookies = context.cookies() or []
        with open(cookies_path, "wb") as f:
            pickle.dump(cookies, f)

        print(f"Куки сохранены в {cookies_path}", flush=True)
        context.close()
        browser.close()


if __name__ == "__main__":
    main()