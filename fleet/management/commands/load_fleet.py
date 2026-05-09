from django.core.management.base import BaseCommand, CommandError

from fleet.models import Ship
from fleet.services.fleet_loader import load_fleet_data


class Command(BaseCommand):
    help = "Load ports, ships, and navigable water from fleet.json"

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, help="Path to fleet.json")

    def handle(self, *args, **options):
        result = load_fleet_data(path=options.get("path"))
        expected_ship_count = result["ships"]
        actual_ship_count = Ship.objects.count()

        if expected_ship_count != 15:
            raise CommandError(
                f"Expected 15 ships in fleet.json, found {expected_ship_count}."
            )

        if actual_ship_count != expected_ship_count:
            raise CommandError(
                "Ship count mismatch after load: "
                f"expected {expected_ship_count}, got {actual_ship_count}."
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Fleet data loaded. "
                f"Ports: {result['ports']}, Ships: {result['ships']}, "
                f"Water points: {result['navigable_water_points']}"
            )
        )
