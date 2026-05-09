from django.core.management.base import BaseCommand

from fleet.models import Ship


class Command(BaseCommand):
	help = "Assign captains to all ships"

	def handle(self, *args, **options):
		captains = [
			"Captain John Smith",
			"Captain Jane Doe",
			"Captain Ahmed Hassan",
			"Captain Maria Garcia",
			"Captain Chen Wei",
			"Captain Rajesh Kumar",
			"Captain Sofia Petrov",
			"Captain Emma Anderson",
			"Captain Hassan Al-Mansouri",
			"Captain Yuki Tanaka",
		]

		ships = Ship.objects.all()
		for idx, ship in enumerate(ships):
			ship.assigned_captain = captains[idx % len(captains)]
			ship.save(update_fields=["assigned_captain"])

		self.stdout.write(
			self.style.SUCCESS(
				f"Assigned captains to {ships.count()} ships"
			)
		)
