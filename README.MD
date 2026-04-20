# CONFIGURATOR.WEB
- Сервис подбора ПК по бюджету

## Статус проекта 
- Проект в активной разработке
---
### Функционал
- [x] Парсинг цен комплектующих
- [x] Подбор конфигураций по бюджету
- [ ] Расчет приблизительного FPS в играх
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


