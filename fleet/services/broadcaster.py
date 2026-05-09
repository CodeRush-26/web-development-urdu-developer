from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


GROUP_NAME = "fleet_updates"


def broadcast_ship_positions() -> None:
    from fleet.models import Ship

    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    payload = list(
        Ship.objects.values(
            "ship_id",
            "name",
            "latitude",
            "longitude",
            "heading",
            "speed",
            "destination_id",
            "fuel",
            "cargo",
            "status",
        )
    )

    async_to_sync(channel_layer.group_send)(
        GROUP_NAME,
        {
            "type": "ship.update",
            "payload": payload,
        },
    )


def broadcast_alerts() -> None:
    from fleet.models import Alert

    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    alerts = list(
        Alert.objects.filter(active=True)
        .order_by("-created_at")
        .values(
            "id",
            "alert_type",
            "severity",
            "message",
            "ship_id",
            "zone_id",
            "details",
            "created_at",
        )
    )[:50]

    for alert in alerts:
        alert["created_at"] = alert["created_at"].isoformat()

    async_to_sync(channel_layer.group_send)(
        GROUP_NAME,
        {
            "type": "alert.update",
            "payload": alerts,
        },
    )
