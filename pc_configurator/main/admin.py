from django.contrib import admin
from .models import SupportRequest


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'topic', 'is_processed', 'created_at')
    list_filter = ('topic', 'is_processed', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)
