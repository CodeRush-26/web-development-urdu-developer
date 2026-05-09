from django.http import JsonResponse

from fleet.models import Ship


def ship_positions(request):
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
