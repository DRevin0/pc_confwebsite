# builder/budget_builder.py (с отладкой)
from components.models import Component
from .compatibility import (
    cpu_motherboard_compatible,
    ram_motherboard_compatible,
    motherboard_case_compatible,
    cooler_cpu_compatible,
    psu_sufficient,
)

def build_by_budget(budget: float):
    return None