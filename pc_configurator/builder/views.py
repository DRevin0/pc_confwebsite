from django.shortcuts import render
from django import forms
from .budget_builder import build_by_budget
from analyzer.services import get_fps_for_gpu
from analyzer.utils import normalize_gpu_name
from collections import defaultdict

RESOLUTION_TABS = [
    {"key": "1080p", "label": "1080p", "hint": "Full HD"},
    {"key": "1440p", "label": "1440p", "hint": "2K"},
    {"key": "4k", "label": "4K", "hint": "Ultra HD"},
]

PRESET_ORDER = ["low", "medium", "high", "ultra", "epic"]
PRESET_LABELS = {
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "ultra": "Ultra",
    "epic": "Epic",
}
PRESET_PRIORITY = {preset: index for index, preset in enumerate(PRESET_ORDER)}


class BudgetForm(forms.Form):
    budget = forms.DecimalField(
        label="Ваш бюджет (₽)",
        min_value=1000,
        max_value=500000,
        initial=50000,
        help_text="Введите сумму в рублях",
        widget=forms.NumberInput(
            attrs={"class": "form-control form-control-lg", "placeholder": "50000"}
        ),
    )


def _fps_level(fps_min: int) -> dict:
    if fps_min < 55:
        return {"label": "Тяжело", "class": "danger", "color": "#f87171"}
    if fps_min <= 90:
        return {"label": "Играбельно", "class": "warning", "color": "#facc15"}
    return {"label": "Комфортно", "class": "success", "color": "#4ade80"}


def _fps_display(fps_min: int, fps_max: int) -> str:
    if fps_min == fps_max:
        return str(fps_min)
    return f"{fps_min}–{fps_max}"


def _parse_resolution(raw_resolution: str) -> tuple[str | None, str | None]:
    raw = (raw_resolution or "").lower().replace("_", "").replace("-", "")

    if raw.startswith("fullhd") or raw.startswith("1080"):
        resolution = "1080p"
        preset = raw.replace("fullhd", "").replace("1080p", "").replace("1080", "")
    elif raw.startswith("2k") or raw.startswith("1440"):
        resolution = "1440p"
        preset = raw.replace("2k", "").replace("1440p", "").replace("1440", "")
    elif raw.startswith("4k") or raw.startswith("2160"):
        resolution = "4k"
        preset = raw.replace("4k", "").replace("2160p", "").replace("2160", "")
    else:
        return None, None

    return resolution, preset if preset in PRESET_ORDER else None


def _row_status(row: dict) -> dict:
    values = [
        preset_data["fps_min"]
        for preset_data in row["presets"].values()
        if preset_data is not None
    ]
    if not values:
        return {"label": "Нет данных", "class": "muted", "color": "#94a3b8"}
    return _fps_level(min(values))


def _average(values: list[int]) -> int | None:
    if not values:
        return None
    return round(sum(values) / len(values))


def _build_fps_report(fps_list):
    by_resolution = {
        tab["key"]: {
            **tab,
            "rows": [],
            "avg_high": None,
            "avg_all": None,
            "status": {"label": "Нет данных", "class": "muted", "color": "#94a3b8"},
        }
        for tab in RESOLUTION_TABS
    }
    grouped = defaultdict(lambda: defaultdict(dict))
    all_values = []

    for row in fps_list:
        resolution, preset = _parse_resolution(row.resolution)
        if not resolution or not preset:
            continue

        level = _fps_level(row.fps_min)
        grouped[resolution][row.game][preset] = {
            "fps_min": row.fps_min,
            "fps_max": row.fps_max,
            "display": _fps_display(row.fps_min, row.fps_max),
            "class": level["class"],
            "color": level["color"],
        }
        all_values.append(row.fps_min)

    for resolution, games in grouped.items():
        rows = []
        high_values = []
        resolution_values = []

        for game, presets in sorted(games.items()):
            ordered_presets = {preset: presets.get(preset) for preset in PRESET_ORDER}
            row_values = [
                value["fps_min"] for value in ordered_presets.values() if value
            ]
            resolution_values.extend(row_values)
            if presets.get("high"):
                high_values.append(presets["high"]["fps_min"])

            table_row = {
                "game": game,
                "game_search": game.lower(),
                "presets": ordered_presets,
            }
            table_row["status"] = _row_status(table_row)
            rows.append(table_row)

        rows.sort(
            key=lambda item: (
                PRESET_PRIORITY.get("high", 0),
                item["status"]["label"],
                item["game"],
            )
        )

        avg_high = _average(high_values)
        avg_all = _average(resolution_values)
        status_value = avg_high if avg_high is not None else avg_all
        by_resolution[resolution].update(
            {
                "rows": rows,
                "avg_high": avg_high,
                "avg_all": avg_all,
                "status": (
                    _fps_level(status_value)
                    if status_value is not None
                    else by_resolution[resolution]["status"]
                ),
            }
        )

    best_tab = max(
        by_resolution.values(),
        key=lambda tab: tab["avg_high"] or tab["avg_all"] or 0,
    )
    summary_avg = best_tab["avg_high"] or best_tab["avg_all"]

    return {
        "tabs": list(by_resolution.values()),
        "preset_labels": [PRESET_LABELS[preset] for preset in PRESET_ORDER],
        "preset_keys": PRESET_ORDER,
        "summary": {
            "game_count": len({row.game for row in fps_list}),
            "sample_count": len(all_values),
            "best_resolution": best_tab["label"],
            "avg_fps": summary_avg,
            "status": best_tab["status"],
        },
    }


def build_view(request):
    build = None
    fps_report = None
    error_message = None

    if request.method == "POST":
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.cleaned_data["budget"]
            build = build_by_budget(budget)

            if build is None:
                error_message = "Не удалось собрать ПК на указанный бюджет. Попробуйте увеличить бюджет."
            else:
                gpu_item = next(
                    item
                    for item in build["items"]
                    if item["component"].category == "gpu"
                )
                gpu_name = normalize_gpu_name(gpu_item["component"].name)
                fps_raw = get_fps_for_gpu(gpu_name)
                if fps_raw:
                    fps_report = _build_fps_report(fps_raw)

    else:
        form = BudgetForm()

    # Разворачиваем build-словарь в отдельные переменные,
    # чтобы в шаблоне не было конфликта build.items (dict-метод vs ключ)
    build_items = build["items"] if build else None
    build_total = build["total"] if build else None
    build_budget = build["budget"] if build else None

    return render(
        request,
        "builder/build_form.html",
        {
            "form": form,
            "build_items": build_items,
            "build_total": build_total,
            "build_budget": build_budget,
            "fps": fps_report,
            "error_message": error_message,
        },
    )
