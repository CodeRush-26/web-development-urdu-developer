from fleet.models import Alert, RestrictedZone, Ship


def create_geofence_alert(ship: Ship, zone: RestrictedZone) -> Alert:
    message = f"{ship.name} entered restricted zone {zone.name}."
    alert, _created = Alert.objects.get_or_create(
        alert_type="geofence",
        ship=ship,
        zone=zone,
        active=True,
        defaults={
            "severity": "critical",
            "message": message,
        },
    )
    return alert
