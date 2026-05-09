from django.urls import path

from fleet import views

urlpatterns = [
    path("", views.map_view, name="map"),
    path("health/", views.health, name="health"),
    path("api/ships/", views.ship_positions, name="ship_positions"),
    path("api/ports/", views.ports, name="ports"),
    path("api/navigable-water/", views.navigable_water, name="navigable_water"),
    path("api/zones/", views.zones, name="zones"),
    path("api/zones/<int:zone_id>/", views.zone_detail, name="zone_detail"),
    path("api/alerts/", views.alerts, name="alerts"),
    path("api/distress/", views.distress, name="distress"),
    path("api/distress/resolve/", views.distress_resolve, name="distress_resolve"),
]
