import math
from dataclasses import dataclass

from django.db import transaction

from fleet.models import RestrictedZone, Ship
from fleet.services.alerts import create_geofence_alert
from fleet.services.geofence import point_in_polygon
from fleet.services.routing import compute_reroute_heading


@dataclass(frozen=True)
class SimulationResult:
    moved: int
    stopped: int


def _knots_to_nm_per_second(speed_knots: float) -> float:
    return speed_knots / 3600.0


def _bearing_to_unit_vector(heading_degrees: float) -> tuple[float, float]:
    radians = math.radians(heading_degrees % 360)
    north = math.cos(radians)
    east = math.sin(radians)
    return north, east


def _apply_motion(lat: float, lon: float, heading: float, speed: float) -> tuple[float, float]:
    distance_nm = _knots_to_nm_per_second(speed)
    north, east = _bearing_to_unit_vector(heading)

    delta_north_nm = north * distance_nm
    delta_east_nm = east * distance_nm

    delta_lat = delta_north_nm / 60.0
    lat_radians = math.radians(lat)
    cos_lat = math.cos(lat_radians) or 1e-6
    delta_lon = delta_east_nm / (60.0 * cos_lat)

    return lat + delta_lat, lon + delta_lon


def _fuel_burn_per_second(speed_knots: float) -> float:
    base_burn_per_hour = 2.0
    speed_burn_per_hour = speed_knots * 0.3
    return (base_burn_per_hour + speed_burn_per_hour) / 3600.0


def simulate_tick() -> SimulationResult:
    moved = 0
    stopped = 0
    to_update = []
    zones = list(RestrictedZone.objects.all())

    with transaction.atomic():
        ships = list(Ship.objects.select_for_update())
        for ship in ships:
            if ship.fuel <= 0:
                if ship.status != "dead-in-water":
                    ship.status = "dead-in-water"
                    to_update.append(ship)
                stopped += 1
                continue

            new_lat, new_lon = _apply_motion(
                lat=ship.latitude,
                lon=ship.longitude,
                heading=ship.heading,
                speed=ship.speed,
            )

            ship.latitude = new_lat
            ship.longitude = new_lon
            ship.fuel = max(0.0, ship.fuel - _fuel_burn_per_second(ship.speed))
            if ship.fuel == 0.0:
                ship.status = "dead-in-water"
            else:
                ship.status = "normal"

            for zone in zones:
                if point_in_polygon((ship.latitude, ship.longitude), zone.polygon):
                    create_geofence_alert(ship, zone)
                    ship.status = "rerouting"
                    ship.heading = compute_reroute_heading(
                        ship.latitude, ship.longitude, zone.polygon
                    )
                    break

            to_update.append(ship)
            moved += 1

        if to_update:
            Ship.objects.bulk_update(
                to_update, ["latitude", "longitude", "fuel", "status", "heading"]
            )

    return SimulationResult(moved=moved, stopped=stopped)
