from django.contrib import admin
from .models import GPUFPS

@admin.register(GPUFPS)
class GPUFPSAdmin(admin.ModelAdmin):
    list_display = ("gpu_name", "game", "resolution", "fps_min", "fps_max", "updated_at")
    list_filter = ("gpu_name", "resolution")
