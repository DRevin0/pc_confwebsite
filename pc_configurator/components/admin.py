from django.contrib import admin
from .models import Component, Price, Spec

@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'url', 'created_at', 'updated_at')
    list_filter = ('category',)
    search_fields = ('name', 'url')

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('component', 'price', 'recorded_at')
    list_filter = ('recorded_at',)
    search_fields = ('component__name',)

@admin.register(Spec)
class SpecAdmin(admin.ModelAdmin):
    list_display = ('component', 'key', 'value')
    list_filter = ('component__category',)
    search_fields = ('component__name', 'key', 'value')