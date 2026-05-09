from datetime import timedelta

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone

from fleet.models import Ship, SimulationState
from fleet.services.simulator import simulate_tick


def ship_positions(request):
	now = timezone.now()
	with transaction.atomic():
		state, _created = SimulationState.objects.select_for_update().get_or_create(
			key="default"
		)
		if state.last_tick is None or now - state.last_tick >= timedelta(seconds=1):
			simulate_tick()
			state.last_tick = now
			state.save(update_fields=["last_tick"])

	ships = list(
		Ship.objects.values(
			"ship_id",
			"name",
			"latitude",
			"longitude",
			"heading",
			"speed",
			"destination_id",
			"fuel",
			"status",
		)
	)
	return JsonResponse({"ships": ships})


def home(request):
	return JsonResponse({"status": "ok", "message": "Fleet API running."})
