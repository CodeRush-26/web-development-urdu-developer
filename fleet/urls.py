from django.urls import path

from fleet import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/ships/", views.ship_positions, name="ship_positions"),
]
