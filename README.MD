# PCONFIGURATOR.WEB
- Сервис подбора ПК по бюджету

## Статус проекта 
- Проект в активной разработке
---
### Функционал
- [ ] Парсинг цен комплектующих
- [ ] Подбор конфигураций по бюджету
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
---
### Структура проекта
```text
pc_configurator/                                    
├── config/                 # Настройки Django      
├── main/                   # Основное приложение   
├── scrapers/               # Scrapy парсеры        
│   ├── spiders/            # Пауки для сайтов      
│   ├── middlewares.py      # User-Agent ротация    
│   └── settings.py         # Настройки Scrapy      
├── requirements.txt        # Зависимости           
├── manage.py               # Django CLI            
└── README.md                                       
```
