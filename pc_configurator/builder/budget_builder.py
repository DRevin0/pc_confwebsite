from decimal import Decimal
from components.models import Component
from .compatibility import (
    cpu_motherboard_compatible,
    ram_motherboard_compatible,
    cooler_cpu_compatible,
    psu_sufficient,
)

BUDGET_RATIOS = {
    'gpu':         Decimal('0.35'),
    'cpu':         Decimal('0.20'),
    'motherboard': Decimal('0.12'),
    'ram':         Decimal('0.08'),
    'ssd':         Decimal('0.08'),
    'psu':         Decimal('0.07'),
    'case':        Decimal('0.06'),
    'cooling':     Decimal('0.04'),
}

REQUIRED_CATEGORIES = {'cpu', 'motherboard', 'gpu', 'ram', 'ssd'}


def _candidates_in_budget(category: str, max_price: Decimal):
    result = []
    for comp in Component.objects.filter(category=category).prefetch_related('prices'):
        price_obj = comp.prices.first()
        if price_obj and price_obj.price <= max_price:
            result.append((comp, price_obj))
    return sorted(result, key=lambda x: x[1].price)


def _best_in_budget(category: str, max_price: Decimal):
    candidates = _candidates_in_budget(category, max_price)
    return candidates[-1] if candidates else (None, None)


def _cheapest_in_budget(category: str, max_price: Decimal):
    candidates = _candidates_in_budget(category, max_price)
    return candidates[0] if candidates else (None, None)


def build_by_budget(budget: float):
    budget = Decimal(str(budget))
    alloc = {cat: budget * ratio for cat, ratio in BUDGET_RATIOS.items()}

    cpu_candidates = list(reversed(_candidates_in_budget('cpu', alloc['cpu'])))
    mb_candidates  = list(reversed(_candidates_in_budget('motherboard', alloc['motherboard'])))
    ram_candidates = list(reversed(_candidates_in_budget('ram', alloc['ram'])))

    picked = {}
    price_objs = {}
    found = False

    for cpu, cpu_po in cpu_candidates:
        for mb, mb_po in mb_candidates:
            if not cpu_motherboard_compatible(cpu, mb):
                continue

            ram_comp = ram_po = None
            for ram, rpo in ram_candidates:
                if ram_motherboard_compatible(ram, mb):
                    ram_comp, ram_po = ram, rpo
                    break
            if ram_comp is None and ram_candidates:
                ram_comp, ram_po = ram_candidates[0]

            picked = {'cpu': cpu, 'motherboard': mb}
            price_objs = {'cpu': cpu_po, 'motherboard': mb_po}
            if ram_comp:
                picked['ram'] = ram_comp
                price_objs['ram'] = ram_po
            found = True
            break
        if found:
            break

    if not found:
        return None

    def _spent():
        return sum(po.price for po in price_objs.values())

    gpu_comp, gpu_po = _best_in_budget('gpu', alloc['gpu'])
    if gpu_comp is None:
        gpu_comp, gpu_po = _cheapest_in_budget('gpu', budget - _spent())
    if gpu_comp:
        picked['gpu'] = gpu_comp
        price_objs['gpu'] = gpu_po

    for category in ('ssd', 'psu', 'cooling', 'case'):
        remaining = budget - _spent()
        if remaining <= 0:
            break
        cat_limit = min(alloc[category], remaining)
        comp, po = _best_in_budget(category, cat_limit)
        if comp:
            picked[category] = comp
            price_objs[category] = po

    if not REQUIRED_CATEGORIES.issubset(picked.keys()):
        return None

    return {
        'items': [
            {
                'component': comp,
                'price': price_objs[cat].price,
                'price_date': price_objs[cat].recorded_at,
            }
            for cat, comp in picked.items()
        ],
        'total': _spent(),
        'budget': budget,
    }
