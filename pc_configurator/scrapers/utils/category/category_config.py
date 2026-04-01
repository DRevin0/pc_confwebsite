#CITILINK
REQUIRED_CATEGORIES_KEYS_citilink = [
        "cpu", "motherboard", "gpu", "ssd", "ram", "psu", "cooling", "case"
    ]
CATEGORY_KEYWORDS_citilink = {
        "cpu": ["процессор", "cpu"],
        "motherboard": ["материнск", "материнская плата"],
        "gpu": ["видеокарт", "gpu"],
        "ssd": ["ssd", "твердотельн"],
        "ram": ["оперативн", "памят"],
        "psu": ["блок питания", "питания"],
        "cooling": ["охлажд", "кулер", "cooling"],
        "case": ["корпус", "компьютерные корпуса"],
    }
FALLBACK_CATEGORY_MAP_citilink = {
        "cooling": ["cpu_cooler", "cooler"],
        "ssd": ["ssd_m2", "ssd_sata"],
    }
CATEGORY_DB_MAP_citilink = {
        "ssd": "ssd",
        "cooling": "cooling",
    }

#YANDEX
REQUIRED_CATEGORIES_KEYS_yandex = [
        "cpu",
        "motherboard",
        "gpu",
        "ssd_sata",
        "ssd_m2",
        "ram",
        "psu",
        "air_cooling",
        "liquid_cooling",
        "case",
    ]
CATEGORY_KEYWORDS_yandex = {
        "cpu": ["процессор", "cpu)"],
        "motherboard": ["материнск", "материнская плата"],
        "gpu": ["видеокарт", "gpu"],
        "ssd_m2": ["m.2", "m2", "ssd m.2", "sata m.2"],
        "ssd_sata": ["sata", "ssd sata"],
        "ram": ["оперативн", "памят"],
        "psu": ["блок питания", "питания"],
        "air_cooling": ["кулер", "воздушн"],
        "liquid_cooling": ["жидкост", "водян", "liquid"],
        "case": ["корпус", "компьютерные корпуса"],
    }
FALLBACK_CATEGORY_MAP_yandex = {
        "ssd_sata": ["ssd_m2", "ssd"],
        "ssd_m2": ["ssd_sata", "ssd"],
        "air_cooling": ["liquid_cooling", "cooling", "кулеры и системы охлаждения"],
        "liquid_cooling": ["air_cooling", "cooling", "кулеры и системы охлаждения"],
    }
CATEGORY_DB_MAP_yandex = {
        "ssd_sata": "ssd",
        "ssd_m2": "ssd",
        "air_cooling": "cooling",
        "liquid_cooling": "cooling",
    }

#DNS
REQUIRED_CATEGORIES_KEYS_dns = [
    "cpu",
    "motherboard",
    "gpu",
    "ssd_sata",
    "ssd_m2",
    "ram",
    "psu",
    "air_cooling",
    "liquid_cooling",
    "case",
]

CATEGORY_KEYWORDS_dns = {
    "cpu": ["процессор", "cpu"],
    "motherboard": ["материнск", "материнская плата"],
    "gpu": ["видеокарт", "gpu"],
    "ssd_sata": ["ssd", "sata"],
    "ssd_m2": ["m.2", "m2", "ssd m.2"],
    "ram": ["оперативн", "памят", "dimm"],
    "psu": ["блок питания", "питания"],
    "air_cooling": ["кулер", "воздушн", "процессор"],
    "liquid_cooling": ["жидкост", "водян", "liquid"],
    "case": ["корпус", "компьютерные корпуса"],
}

FALLBACK_CATEGORY_MAP_dns = {
    "ssd_sata": ["ssd_m2"],
    "ssd_m2": ["ssd_sata"],
    "air_cooling": ["liquid_cooling", "cooling"],
    "liquid_cooling": ["air_cooling", "cooling"],
}

CATEGORY_DB_MAP_dns = {
    "ssd_sata": "ssd",
    "ssd_m2": "ssd",
    "air_cooling": "cooling",
    "liquid_cooling": "cooling",
}