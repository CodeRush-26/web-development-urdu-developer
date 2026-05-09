from django.http import JsonResponse
from django.shortcuts import render

from fleet.models import NavigableWater, Port, Ship


def map_view(request):
	return render(request, "fleet/map.html")


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


def ports(request):
	ports_data = list(
		Port.objects.values("code", "name", "latitude", "longitude")
	)
	return JsonResponse({"ports": ports_data})


def navigable_water(request):
	water = NavigableWater.objects.first()
	return JsonResponse({"polygon": water.polygon if water else []})


def health(request):
	return JsonResponse({"status": "ok", "message": "Fleet API running."})
