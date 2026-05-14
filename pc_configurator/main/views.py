from django import forms
from django.shortcuts import render
from .models import SupportRequest


class SupportForm(forms.ModelForm):
    class Meta:
        model = SupportRequest
        fields = ['name', 'email', 'topic', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например, Алексей',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'name@example.com',
            }),
            'topic': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Опишите вопрос или проблему подробнее',
            }),
        }
        labels = {
            'name': 'Ваше имя',
            'email': 'Email для ответа',
            'topic': 'Тема обращения',
            'message': 'Сообщение',
        }

def stub(request):
    form = SupportForm(request.POST or None)
    sent = False

    if request.method == 'POST' and form.is_valid():
        form.save()
        sent = True
        form = SupportForm()

    return render(request, 'main/maintenance.html', {
        'form': form,
        'sent': sent,
    })

def about(request):
    return render(request, 'main/about.html')

def how_it_works(request):
    return render(request, 'main/how_it_works.html')

def homepage(request):
    return render(request, 'main/homepage.html')
