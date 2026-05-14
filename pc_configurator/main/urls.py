from django.urls import path
from . import views

urlpatterns = [
    path("maintenance/", views.stub, name="support"),
    path("how-it-works/", views.how_it_works, name="how_it_works"),
    path("about/", views.about, name="about"),
    path("", views.homepage, name="homepage"),
]
