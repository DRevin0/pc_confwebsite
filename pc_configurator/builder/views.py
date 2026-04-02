from django.shortcuts import render
from django import forms
from .budget_builder import build_by_budget

class BudgetForm(forms.Form):
    budget = forms.DecimalField(
        label='Ваш бюджет (₽)',
        min_value=1000,
        max_value=500000,
        initial=50000,
        help_text='Введите сумму в рублях',
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'placeholder': '50000'}),
    )

def build_view(request):
    build = None
    error_message = None
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.cleaned_data['budget']
            build = build_by_budget(budget)
            if build is None:
                error_message = 'Не удалось собрать ПК на указанный бюджет. Попробуйте увеличить бюджет.'
    else:
        form = BudgetForm()
    return render(request, 'builder/build_form.html', {
        'form': form,
        'build': build,
        'error_message': error_message
    })
