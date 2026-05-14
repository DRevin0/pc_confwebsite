import re
from components.models import Component

_SOCKETS = [
    "LGA1851",
    "LGA1700",
    "LGA1200",
    "LGA1151",
    "LGA1150",
    "LGA1155",
    "LGA1156",
    "AM5",
    "AM4",
    "AM3+",
    "AM3",
]

_CHIPSET_TO_SOCKET = {
    "A620": "AM5",
    "B650": "AM5",
    "X670": "AM5",
    "A320": "AM4",
    "A520": "AM4",
    "B350": "AM4",
    "B450": "AM4",
    "B550": "AM4",
    "X370": "AM4",
    "X470": "AM4",
    "X570": "AM4",
    "H610": "LGA1700",
    "B660": "LGA1700",
    "H670": "LGA1700",
    "Z690": "LGA1700",
    "B760": "LGA1700",
    "H770": "LGA1700",
    "Z790": "LGA1700",
    "H410": "LGA1200",
    "H470": "LGA1200",
    "B460": "LGA1200",
    "B560": "LGA1200",
    "Z490": "LGA1200",
    "Z590": "LGA1200",
    "H510": "LGA1200",
    "H310": "LGA1151",
    "H370": "LGA1151",
    "B360": "LGA1151",
    "Z370": "LGA1151",
    "Z390": "LGA1151",
}

_FORM_FACTORS = ("E-ATX", "MICRO-ATX", "M-ATX", "MATX", "MINI-ITX", "ATX", "ITX")


def _normalize_socket(text: str) -> str:
    return re.sub(r"\s+", "", text.upper())


def get_spec(component: Component, *keys: str) -> str | None:
    for key in keys:
        spec = component.specs.filter(key__icontains=key).first()
        if spec:
            return spec.value
    return None


def get_int_spec(component: Component, *keys: str, default=None) -> int | None:
    value = get_spec(component, *keys)
    if value:
        match = re.search(r"\d+", value)
        if match:
            return int(match.group())
    return default


def get_socket(component: Component) -> str | None:
    val = get_spec(component, "Сокет", "Socket", "socket")
    if val:
        val_norm = _normalize_socket(val)
        for socket in _SOCKETS:
            if _normalize_socket(socket) in val_norm:
                return socket

    name_norm = _normalize_socket(component.name)
    for socket in _SOCKETS:
        if _normalize_socket(socket) in name_norm:
            return socket

    name_upper = component.name.upper()
    for chipset, socket in _CHIPSET_TO_SOCKET.items():
        if chipset in name_upper:
            return socket

    return None


def _detect_ddr(text: str) -> str | None:
    text_upper = text.upper()
    for ddr in ("DDR5", "DDR4", "DDR3"):
        if ddr in text_upper:
            return ddr
    return None


def get_ram_type_from_motherboard(component: Component) -> str | None:
    val = get_spec(component, "Тип памяти", "Поддерживаемые типы", "Память")
    if val:
        return _detect_ddr(val)
    return _detect_ddr(component.name)


def get_ram_type_from_ram(component: Component) -> str | None:
    val = get_spec(component, "Тип памяти", "Тип", "Type")
    if val:
        ddr = _detect_ddr(val)
        if ddr:
            return ddr
    return _detect_ddr(component.name)


def get_cpu_tdp(component: Component) -> int:
    return get_int_spec(
        component, "TDP", "Тепловыделение", "Потребляемая мощность", default=65
    )


def get_gpu_power_recommended(component: Component) -> int:
    return get_int_spec(
        component,
        "Рекомендуемая мощность БП",
        "Потребляемая мощность",
        "TDP",
        default=150,
    )


def get_psu_power(component: Component) -> int | None:
    return get_int_spec(component, "Номинальная мощность", "Мощность")


def get_cooler_supported_sockets(component: Component) -> list[str]:
    val = get_spec(
        component, "Совместимые сокеты", "Поддерживаемые сокеты", "Сокет", "Socket"
    )
    if val:
        return [s.strip().upper() for s in re.split(r"[,/;]", val) if s.strip()]
    return []


def _normalize_ff(ff: str) -> str:
    return (
        ff.upper()
        .replace("MICRO-ATX", "MATX")
        .replace("M-ATX", "MATX")
        .replace("MINI-ITX", "ITX")
    )


def get_motherboard_form_factor(component: Component) -> str | None:
    val = get_spec(component, "Форм-фактор", "Form Factor", "Формат")
    if val:
        val_upper = val.upper()
        for ff in _FORM_FACTORS:
            if ff in val_upper:
                return _normalize_ff(ff)
    return None


def get_case_supported_form_factors(component: Component) -> list[str]:
    val = get_spec(
        component,
        "Совместимые форм-факторы",
        "Форм-факторы плат",
        "Поддерживаемые форм-факторы",
        "Форм-фактор",
    )
    if val:
        val_upper = val.upper()
        return [_normalize_ff(ff) for ff in _FORM_FACTORS if ff in val_upper]
    return []
