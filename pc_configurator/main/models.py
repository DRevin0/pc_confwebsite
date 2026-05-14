from django.db import models


class SupportRequest(models.Model):
    TOPIC_CHOICES = [
        ("question", "Вопрос по работе сайта"),
        ("bug", "Нашел ошибку"),
        ("data", "Проблема с ценами или характеристиками"),
        ("feature", "Предложение по улучшению"),
        ("other", "Другое"),
    ]
    STATUS_CHOICES = [
        ("new", "Новое"),
        ("in_progress", "В работе"),
        ("done", "Обработано"),
    ]

    name = models.CharField(max_length=80, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    contact = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Дополнительный контакт",
        help_text="Телефон, Telegram или другой удобный способ связи",
    )
    topic = models.CharField(max_length=20, choices=TOPIC_CHOICES, verbose_name="Тема")
    subject = models.CharField(
        max_length=140, default="Без темы", verbose_name="Краткое описание"
    )
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата обращения")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name="Статус",
    )
    admin_comment = models.TextField(
        blank=True, verbose_name="Комментарий администратора"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Обращение в поддержку"
        verbose_name_plural = "Обращения в поддержку"

    def __str__(self):
        return f"{self.name} - {self.subject}"
