# CONFIGURATOR.WEB
- Сервис подбора ПК по бюджету

## Статус проекта 
- Ver 1.2
---
### Функционал
- [x] Парсинг цен комплектующих
- [x] Подбор конфигураций по бюджету
- [x] Расчет приблизительного FPS в играх
---
### Стек
| Технология | Версия | 
|------------|--------|
| Python | 3.14.3 | 
| Django | 4.2.29 | 
| Scrapy | 2.14.1 | 
| SQLite | - | 
| fake-useragent | 2.2.0 |
| undetected_chromedriver | 3.5.5 |
| playwright | 1.58.0 |

---
### Структура проекта
```text
data/	                    # База данных
pc_configurator/   
├── analyzer/               # Анализ фпс    
├── config/                 # Настройки Django     
├── builder/                # Создание виртуальной сборки
├── components/             
├── main/                   # Основное приложение   
├── scrapers/               # Scrapy парсеры        
│   ├── spiders/            # Пауки для сайтов      
│   ├── middlewares.py      # User-Agent ротация    
│   └── settings.py         # Настройки Scrapy      
├── requirements.txt        # Зависимости           
├── manage.py   			# Django CLI
├──	run_dns_parser			# Запуск парсера для DNS               
├── run_citilink_parser		# Запуск парсера для Ситилинк
├── run_yandex...           # Запуск парсера для Яндекс Маркета
├── run_gpu_parser          # Запуск парсера для анализа фпс
└── README.md                                        
```
---
###   -  Запуск через Docker
1. **Клонируйте репозиторий** и перейдите в папку проекта:
 ```bash
git clone https://github.com/DRevin0/pc_confwebsite
cd pc_confwebsite
```
2. **Запустите подготовленный скрипт**:
 ```bash
chmod +x deploy_and_enter.sh
./deploy_and_enter.sh
```
3. **Скрипт** соберет образ, запустит контейнер, выполнит миграции и запустит сервер. 
###    - Запуск локально
1. **Клонируйте репозиторий** и перейдите в папку проекта:
 ```bash
git clone https://github.com/DRevin0/pc_confwebsite
cd pc_confwebsite
```
2. **Установите зависимости**:
 ```bash
pip install -r pc_configurator/requirements.txt
playwright install chromium
playwright install-deps chromium   # для Linux
```
3. **Выполните миграции и запустите сервер** :
 ```bash
cd pc_configurator
python manage.py migrate
python manage.py runserver
```

