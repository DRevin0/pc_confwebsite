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
    cpu_socket = get_socket(cpu)
    mb_socket = get_socket(motherboard)
    if cpu_socket and mb_socket:
        return cpu_socket == mb_socket
    if cpu_socket and not mb_socket:
        return False  
    return True  


def ram_motherboard_compatible(ram: Component, motherboard: Component) -> bool:
    ram_type = get_ram_type_from_ram(ram)
    mb_ram_type = get_ram_type_from_motherboard(motherboard)
    if ram_type and mb_ram_type:
        return ram_type == mb_ram_type
    return True


def motherboard_case_compatible(motherboard: Component, case: Component) -> bool:
    mb_ff = get_motherboard_form_factor(motherboard)
    case_ffs = get_case_supported_form_factors(case)
    if mb_ff and case_ffs:
        return mb_ff in case_ffs
    return True


def cooler_cpu_compatible(cooler: Component, cpu: Component) -> bool:
    cpu_socket = get_socket(cpu)
    cooler_sockets = get_cooler_supported_sockets(cooler)
    if cpu_socket and cooler_sockets:
        return cpu_socket in cooler_sockets
    return True


def psu_sufficient(psu: Component, cpu: Component, gpu: Component) -> bool:
    psu_power = get_psu_power(psu)
    if psu_power:
        required = get_cpu_tdp(cpu) + get_gpu_power_recommended(gpu) + 100
        return psu_power >= required
    return True