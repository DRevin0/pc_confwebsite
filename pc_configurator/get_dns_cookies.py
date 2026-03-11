import undetected_chromedriver as uc
import pickle
def main():
    # Запускаем браузер (headless=False, чтобы видеть процесс)
    driver = uc.Chrome(headless=False)
    
    # Переходим на страницу каталога процессоров
    url = 'https://www.dns-shop.ru/catalog/17a899cd16404e77/processory/'
    driver.get(url)
    
    print("Браузер открыт. Если появится капча, пройдите её вручную.")
    print("После успешной загрузки страницы нажмите Enter здесь...")
    input()  # ждём ручного подтверждения
    
    # Сохраняем куки
    with open('dns_cookies.pkl', 'wb') as f:
        pickle.dump(driver.get_cookies(), f)
    
    print("Куки сохранены в dns_cookies.pkl")
    driver.quit()

if __name__ == '__main__':
    main()