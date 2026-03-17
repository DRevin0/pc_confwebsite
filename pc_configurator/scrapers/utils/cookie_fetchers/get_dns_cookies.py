import undetected_chromedriver as uc
import pickle
from pathlib import Path
def main():

    cookies_dir = Path(__file__).parent.parent.parent / "cookies"
    cookies_dir.mkdir(exist_ok=True)
    cookies_path = cookies_dir / "dns_cookies.pkl"

    # Запускаем браузер (headless=False, чтобы видеть процесс)
    driver = uc.Chrome(headless=False)
    
    # Переходим на страницу каталога процессоров
    url = 'https://www.dns-shop.ru/catalog/17a899cd16404e77/processory/'
    driver.get(url)
    
    print("Браузер открыт. Если появится капча, пройдите её вручную.")
    print("После успешной загрузки страницы нажмите Enter здесь...")
    input()  # ждём ручного подтверждения
    
    cookies = driver.get_cookies()
    if cookies is None:
        cookies = []
    # Сохраняем куки
    with open(cookies_path, 'wb') as f:
        pickle.dump(cookies, f)
    
    print("Куки сохранены в dns_cookies.pkl")
    driver.quit()

if __name__ == '__main__':
    main()