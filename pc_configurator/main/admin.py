from django.contrib import admin
from .models import SupportRequest


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "topic", "status", "created_at")
    list_filter = ("topic", "status", "created_at")
    search_fields = ("subject", "name", "email", "contact", "message")
    readonly_fields = ("created_at",)
    list_editable = ("status",)
    fieldsets = (
        (
            "Данные обращения",
            {"fields": ("name", "email", "contact", "topic", "subject", "message")},
        ),
        ("Обработка", {"fields": ("status", "admin_comment", "created_at")}),
    )
