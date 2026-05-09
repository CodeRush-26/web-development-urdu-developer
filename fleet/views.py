import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from fleet.models import NavigableWater, Port, RestrictedZone, Ship


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
			"cargo",
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


@csrf_exempt
def zones(request):
	if request.method == "GET":
		zones_data = list(
			RestrictedZone.objects.values("id", "name", "polygon")
		)
		return JsonResponse({"zones": zones_data})

	if request.method == "POST":
		payload = json.loads(request.body or "{}")
		name = payload.get("name") or "Restricted Zone"
		polygon = payload.get("polygon") or []
		zone = RestrictedZone.objects.create(name=name, polygon=polygon)
		return JsonResponse({"id": zone.id, "name": zone.name, "polygon": zone.polygon})

	return JsonResponse({"error": "method_not_allowed"}, status=405)


@csrf_exempt
def zone_detail(request, zone_id: int):
	try:
		zone = RestrictedZone.objects.get(id=zone_id)
	except RestrictedZone.DoesNotExist:
		return JsonResponse({"error": "not_found"}, status=404)

	if request.method == "PUT":
		payload = json.loads(request.body or "{}")
		zone.name = payload.get("name", zone.name)
		zone.polygon = payload.get("polygon", zone.polygon)
		zone.save(update_fields=["name", "polygon"])
		return JsonResponse({"id": zone.id, "name": zone.name, "polygon": zone.polygon})

	if request.method == "DELETE":
		zone.delete()
		return JsonResponse({"deleted": True})

	return JsonResponse({"error": "method_not_allowed"}, status=405)


def health(request):
	return JsonResponse({"status": "ok", "message": "Fleet API running."})
