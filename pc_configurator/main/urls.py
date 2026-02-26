from django.urls import path
from . import views

urlpatterns = [
    path('maintenance/', views.stub),
    path('about/', views.about, name='about'),
    path('', views.homepage, name='homepage'),
] 