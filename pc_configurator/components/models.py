from django.db import models


class Component(models.Model):
    CATEGORY_CHOICES = [
        ("cpu", "Процессор"),
        ("motherboard", "Материнская плата"),
        ("gpu", "Видеокарта"),
        ("ssd", "SSD"),
        ("ram", "Оперативная память"),
        ("psu", "Блок питания"),
        ("cooling", "Охлаждение"),
        ("case", "Корпус"),
    ]

    name = models.CharField(max_length=500, verbose_name="Название")
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, verbose_name="Категория"
    )
    url = models.URLField(unique=True, verbose_name="Ссылка на товар")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def current_price(self):
        price_obj = self.prices.first()
        return price_obj.price if price_obj else None


class Price(models.Model):
    component = models.ForeignKey(
        Component, on_delete=models.CASCADE, related_name="prices"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    recorded_at = models.DateTimeField(auto_now=True, verbose_name="Дата записи")

    class Meta:
        ordering = ["-recorded_at"]
        unique_together = ("component",)


class Spec(models.Model):
    component = models.ForeignKey(
        Component, on_delete=models.CASCADE, related_name="specs"
    )
    key = models.CharField(max_length=200, verbose_name="Характеристика")
    value = models.CharField(max_length=500, verbose_name="Значение")

    class Meta:
        unique_together = ("component", "key")
