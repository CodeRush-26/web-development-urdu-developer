from django.urls import path

from fleet.consumers import FleetConsumer

websocket_urlpatterns = [
    path("ws/fleet/", FleetConsumer.as_asgi()),
]
