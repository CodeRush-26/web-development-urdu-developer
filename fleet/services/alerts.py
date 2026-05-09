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
            "details": {"zone_id": zone.id},
        },
    )
    return alert


def create_proximity_alert(ship: Ship, other_ship: Ship, distance_km: float) -> Alert:
    pair_key = "-".join(sorted([ship.ship_id, other_ship.ship_id]))
    message = f"Proximity warning: {ship.name} and {other_ship.name} within {distance_km:.2f} km."
    alerts = Alert.objects.filter(alert_type="proximity", active=True)
    for alert in alerts:
        if alert.details.get("pair_key") == pair_key:
            alert.message = message
            alert.details = {
                "pair_key": pair_key,
                "ship_ids": [ship.ship_id, other_ship.ship_id],
                "distance_km": round(distance_km, 3),
            }
            alert.save(update_fields=["message", "details"])
            return alert

    return Alert.objects.create(
        alert_type="proximity",
        severity="warning",
        message=message,
        ship=ship,
        details={
            "pair_key": pair_key,
            "ship_ids": [ship.ship_id, other_ship.ship_id],
            "distance_km": round(distance_km, 3),
        },
    )


def resolve_proximity_alerts(active_pair_keys: set[str]) -> None:
    alerts = Alert.objects.filter(alert_type="proximity", active=True)
    for alert in alerts:
        pair_key = alert.details.get("pair_key")
        if pair_key and pair_key not in active_pair_keys:
            alert.active = False
            alert.save(update_fields=["active"])


def create_distress_alert(ship: Ship, parsed: dict, raw_message: str) -> Alert:
    if ship.status != "distress":
        ship.status = "distress"
        ship.save(update_fields=["status"])
    message = f"Distress from {ship.name}: {parsed.get('summary', 'reported issue')}."
    return Alert.objects.create(
        alert_type="distress",
        severity=parsed.get("severity", "warning"),
        message=message,
        ship=ship,
        details={
            "raw": raw_message,
            "problems": parsed.get("problems", []),
            "injuries": parsed.get("injuries"),
            "severity": parsed.get("severity"),
        },
    )
