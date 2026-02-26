from django.urls import path
from . import views

urlpatterns = [
    path('', views.stub),
    path('about/', views.about, name='about'),
] 