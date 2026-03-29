# builder/compatibility.py (заглушки)
from components.models import Component
from .spec_utils import (
    get_socket,
    get_ram_type_from_motherboard,
    get_ram_type_from_ram,
    get_cpu_tdp,
    get_gpu_power_recommended,
    get_psu_power,
    get_cooler_supported_sockets,
    get_motherboard_form_factor,
    get_case_supported_form_factors,
)

def cpu_motherboard_compatible(cpu: Component, motherboard: Component) -> bool:
    # Заглушка: всегда считаем совместимыми
    return True

def ram_motherboard_compatible(ram: Component, motherboard: Component) -> bool:
    # Заглушка: всегда совместимы
    return True

def motherboard_case_compatible(motherboard: Component, case: Component) -> bool:
    # Заглушка: всегда совместимы
    return True

def cooler_cpu_compatible(cooler: Component, cpu: Component) -> bool:
    # Заглушка: всегда совместимы
    return True

def psu_sufficient(psu: Component, cpu: Component, gpu: Component) -> bool:
    # Заглушка: всегда достаточно
    return True