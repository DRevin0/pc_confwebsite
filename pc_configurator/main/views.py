from django import forms
from django.shortcuts import redirect, render
from .models import SupportRequest


class SupportForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'tabindex': '-1',
            'class': 'support-hp',
        }),
    )

    class Meta:
        model = SupportRequest
        fields = ['name', 'email', 'contact', 'topic', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например, Алексей',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'name@example.com',
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Telegram или телефон, если удобно',
            }),
            'topic': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например, не подбирается сборка на 50000 ₽',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Опишите вопрос или проблему подробнее',
            }),
        }
        labels = {
            'name': 'Ваше имя',
            'email': 'Email для ответа',
            'contact': 'Дополнительный контакт',
            'topic': 'Тема обращения',
            'subject': 'Краткое описание',
            'message': 'Сообщение',
        }
        help_texts = {
            'contact': 'Необязательно. Можно оставить пустым.',
        }

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise forms.ValidationError('Форма отправлена некорректно.')
        return value

    def clean_subject(self):
        subject = self.cleaned_data['subject'].strip()
        if len(subject) < 5:
            raise forms.ValidationError('Опишите тему чуть подробнее.')
        return subject

    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        if len(message) < 20:
            raise forms.ValidationError('Сообщение должно быть не короче 20 символов.')
        return message

def stub(request):
    form = SupportForm()

    if request.method == 'POST':
        form = SupportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/maintenance/?sent=1')

    return render(request, 'main/maintenance.html', {
        'form': form,
        'sent': request.GET.get('sent') == '1',
    })

def about(request):
    return render(request, 'main/about.html')

def how_it_works(request):
    return render(request, 'main/how_it_works.html')

def homepage(request):
    return render(request, 'main/homepage.html')
