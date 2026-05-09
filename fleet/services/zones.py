from django.db import transaction

from fleet.models import RestrictedZone, Ship
from fleet.services.alerts import create_geofence_alert
from fleet.services.geofence import point_in_polygon
from fleet.services.routing import compute_reroute_heading


def apply_zone_to_ships(zone: RestrictedZone) -> None:
    ships = list(Ship.objects.all())
    to_update = []

    with transaction.atomic():
        for ship in ships:
            if point_in_polygon((ship.latitude, ship.longitude), zone.polygon):
                create_geofence_alert(ship, zone)
                ship.status = "rerouting"
                ship.heading = compute_reroute_heading(
                    ship.latitude, ship.longitude, zone.polygon
                )
                to_update.append(ship)

        if to_update:
            Ship.objects.bulk_update(to_update, ["status", "heading"])
