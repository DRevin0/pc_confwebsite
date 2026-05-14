from django.db import models


class SupportRequest(models.Model):
    TOPIC_CHOICES = [
        ('question', 'Вопрос по работе сайта'),
        ('bug', 'Нашел ошибку'),
        ('data', 'Проблема с ценами или характеристиками'),
        ('other', 'Другое'),
    ]

    name = models.CharField(max_length=80, verbose_name='Имя')
    email = models.EmailField(verbose_name='Email')
    topic = models.CharField(max_length=20, choices=TOPIC_CHOICES, verbose_name='Тема')
    message = models.TextField(verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата обращения')
    is_processed = models.BooleanField(default=False, verbose_name='Обработано')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Обращение в поддержку'
        verbose_name_plural = 'Обращения в поддержку'

    def __str__(self):
        return f'{self.name} - {self.get_topic_display()}'
