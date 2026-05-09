import time

from django.core.management.base import BaseCommand

from fleet.services.broadcaster import broadcast_alerts, broadcast_ship_positions
from fleet.services.simulator import simulate_tick


class Command(BaseCommand):
    help = "Run the ship simulation loop (1 tick per second)"

    def add_arguments(self, parser):
        parser.add_argument("--ticks", type=int, help="Number of ticks to run")

    def handle(self, *args, **options):
        ticks = options.get("ticks")
        count = 0

        self.stdout.write("Simulation started.")
        while True:
            result = simulate_tick()
            count += 1
            broadcast_ship_positions()
            broadcast_alerts()
            self.stdout.write(
                f"Tick {count}: moved={result.moved}, stopped={result.stopped}"
            )

            if ticks and count >= ticks:
                break

            time.sleep(1)

        self.stdout.write("Simulation finished.")
