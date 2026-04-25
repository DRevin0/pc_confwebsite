from django.shortcuts import render
from django import forms
from .budget_builder import build_by_budget
from analyzer.services import get_fps_for_gpu
from analyzer.utils import normalize_gpu_name
from collections import defaultdict

RESOLUTION_LABELS = {
    'fullhdlow':    {'label': '1080p', 'preset': 'Low',    'color': '#4ade80'},
    'fullhdmedium': {'label': '1080p', 'preset': 'Medium', 'color': '#facc15'},
    'fullhdhigh':   {'label': '1080p', 'preset': 'High',   'color': '#f87171'},
    '2klow':        {'label': '1440p', 'preset': 'Low',    'color': '#4ade80'},
    '2kmedium':     {'label': '1440p', 'preset': 'Medium', 'color': '#facc15'},
    '2khigh':       {'label': '1440p', 'preset': 'High',   'color': '#f87171'},
    '4klow':        {'label': '4K',    'preset': 'Low',    'color': '#4ade80'},
    '4kmedium':     {'label': '4K',    'preset': 'Medium', 'color': '#facc15'},
    '4khigh':       {'label': '4K',    'preset': 'High',   'color': '#f87171'},
}

RESOLUTION_ORDER = [
    'fullhdlow', 'fullhdmedium', 'fullhdhigh',
    '2klow', '2kmedium', '2khigh',
    '4klow', '4kmedium', '4khigh',
]

class BudgetForm(forms.Form):
    budget = forms.DecimalField(
        label='Ваш бюджет (₽)',
        min_value=1000,
        max_value=500000,
        initial=50000,
        help_text='Введите сумму в рублях',
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'placeholder': '50000'}),
    )

def _fps_color(fps_min: int) -> str:
    """Цвет по значению FPS: красный < 55, жёлтый 55–90, зелёный > 90."""
    if fps_min < 55:
        return '#f87171'   # red
    elif fps_min <= 90:
        return '#facc15'   # yellow
    else:
        return '#4ade80'   # green


def _group_fps(fps_list):
    """Группируем FPS по названию игры, добавляем красивые метки разрешений."""
    by_game = defaultdict(list)
    for row in fps_list:
        meta = RESOLUTION_LABELS.get(row.resolution, {
            'label': row.resolution, 'preset': '', 'color': '#94a3b8'
        })
        color = _fps_color(row.fps_min)
        by_game[row.game].append({
            'resolution_raw': row.resolution,
            'label':  meta['label'],
            'preset': meta['preset'],
            'color':  color,
            'fps_min': row.fps_min,
            'fps_max': row.fps_max,
            'fps_display': str(row.fps_min) if row.fps_min == row.fps_max
                           else f"{row.fps_min} – {row.fps_max}",
            'bar_pct': min(100, int(row.fps_min / 2.4)),  # 240 fps = 100%
        })

    result = []
    for game, entries in by_game.items():
        entries.sort(key=lambda e: RESOLUTION_ORDER.index(e['resolution_raw'])
                     if e['resolution_raw'] in RESOLUTION_ORDER else 99)
        result.append({'game': game, 'entries': entries})
    return result



def build_view(request):
    build = None
    fps_grouped = None
    error_message = None

    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.cleaned_data['budget']
            build = build_by_budget(budget)

            if build is None:
                error_message = 'Не удалось собрать ПК на указанный бюджет. Попробуйте увеличить бюджет.'
            else:
                gpu_item = next(
                    item for item in build['items']
                    if item['component'].category == 'gpu'
                )
                gpu_name = normalize_gpu_name(gpu_item['component'].name)
                fps_raw = get_fps_for_gpu(gpu_name)
                if fps_raw:
                    fps_grouped = _group_fps(fps_raw)

    else:
        form = BudgetForm()

    # Разворачиваем build-словарь в отдельные переменные,
    # чтобы в шаблоне не было конфликта build.items (dict-метод vs ключ)
    build_items = build['items'] if build else None
    build_total = build['total']  if build else None
    build_budget = build['budget'] if build else None

    return render(request, 'builder/build_form.html', {
        'form': form,
        'build_items':  build_items,
        'build_total':  build_total,
        'build_budget': build_budget,
        'fps': fps_grouped,
        'error_message': error_message,
    })
