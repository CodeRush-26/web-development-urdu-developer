import json
from pathlib import Path

from django.conf import settings
from django.db import transaction

from fleet.models import NavigableWater, Port, Ship


def _get_data_path(path: str | None) -> Path:
    if path:
        return Path(path)
    return Path(settings.BASE_DIR) / "fleet.json"


def load_fleet_data(path: str | None = None) -> dict:
    data_path = _get_data_path(path)
    with data_path.open("r", encoding="utf-8") as data_file:
        data = json.load(data_file)

    ports = data.get("ports", [])
    ships = data.get("fleet", [])
    polygon = data.get("navigableWater", [])

    with transaction.atomic():
        for port in ports:
            Port.objects.update_or_create(
                code=port["id"],
                defaults={
                    "name": port["name"],
                    "latitude": port["position"][0],
                    "longitude": port["position"][1],
                },
            )

        NavigableWater.objects.update_or_create(
            name="default",
            defaults={
                "polygon": polygon,
            },
        )

        for ship in ships:
            destination = Port.objects.get(code=ship["destination"])
            Ship.objects.update_or_create(
                ship_id=ship["shipId"],
                defaults={
                    "name": ship["name"],
                    "latitude": ship["position"][0],
                    "longitude": ship["position"][1],
                    "speed": ship["speed"],
                    "heading": ship["heading"],
                    "destination": destination,
                    "fuel": ship["fuel"],
                    "cargo": ship["cargo"],
                    "status": ship["status"],
                },
            )

    return {
        "ports": len(ports),
        "ships": len(ships),
        "navigable_water_points": len(polygon),
    }
