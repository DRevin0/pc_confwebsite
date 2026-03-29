# builder/spec_utils.py (заглушка)
from components.models import Component, Spec

def get_spec(component: Component, key: str) -> None:
    return None

def get_int_spec(component: Component, key: str, default=None) -> None:
    return None

def get_socket(component: Component) -> None:
    return None

def get_ram_type_from_motherboard(component: Component) -> None:
    return None

def get_ram_type_from_ram(component: Component) -> None:
    return None

def get_cpu_tdp(component: Component) -> int:
    return 65   # значение по умолчанию, не None

def get_gpu_power_recommended(component: Component) -> int:
    return 150

def get_psu_power(component: Component) -> None:
    return None

def get_cooler_supported_sockets(component: Component) -> list:
    return []

def get_motherboard_form_factor(component: Component) -> None:
    return None

def get_case_supported_form_factors(component: Component) -> list:
    return []