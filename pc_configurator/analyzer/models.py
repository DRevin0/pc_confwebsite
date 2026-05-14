from django.db import models


class GPUFPS(models.Model):
    gpu_name = models.CharField(max_length=255)
    game = models.CharField(max_length=255)
    resolution = models.CharField(max_length=64)  # fullhd, 1440p, 4k +настройки
    fps_min = models.IntegerField()
    fps_max = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.gpu_name} | {self.game} | {self.resolution}"
