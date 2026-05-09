from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from fleet.services.broadcaster import GROUP_NAME


class FleetConsumer(JsonWebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)(GROUP_NAME, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(GROUP_NAME, self.channel_name)

    def ship_update(self, event):
        self.send_json({"type": "ship_update", "ships": event["payload"]})
