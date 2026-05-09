import json
from datetime import timedelta

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from fleet.models import Alert, NavigableWater, Port, RestrictedZone, Ship, ShipSnapshot
from fleet.services.alerts import create_distress_alert
from fleet.services.broadcaster import broadcast_alerts
from fleet.services.nlp import parse_distress
from fleet.services.zones import apply_zone_to_ships


def map_view(request):
	return render(request, "fleet/map.html")


def ship_positions(request):
	role = request.GET.get("role")
	captain_name = request.GET.get("captain_name")
	ship_id = request.GET.get("ship_id")
	
	if role == "captain":
		if not captain_name:
			return JsonResponse({"error": "missing_captain_name"}, status=400)
		# Captain can only see their assigned ship(s)
		ships_qs = Ship.objects.filter(assigned_captain=captain_name)
		if ship_id:
			ships_qs = ships_qs.filter(ship_id=ship_id)
	elif role == "command":
		# Command has full access to all ships
		ships_qs = Ship.objects.all()
		if ship_id:
			ships_qs = ships_qs.filter(ship_id=ship_id)
	else:
		# Default: full access if no role specified
		ships_qs = Ship.objects.all()
		if ship_id:
			ships_qs = ships_qs.filter(ship_id=ship_id)
	
	ships = list(
		ships_qs.values(
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
			"assigned_captain",
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
		apply_zone_to_ships(zone)
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
		apply_zone_to_ships(zone)
		return JsonResponse({"id": zone.id, "name": zone.name, "polygon": zone.polygon})

	if request.method == "DELETE":
		zone.delete()
		return JsonResponse({"deleted": True})

	return JsonResponse({"error": "method_not_allowed"}, status=405)


def alerts(request):
	role = request.GET.get("role")
	captain_name = request.GET.get("captain_name")
	ship_id = request.GET.get("ship_id")
	
	alerts_qs = Alert.objects.filter(active=True)
	
	if role == "captain":
		if not captain_name:
			return JsonResponse({"error": "missing_captain_name"}, status=400)
		# Captain can only see alerts for their assigned ship(s)
		captain_ships = Ship.objects.filter(assigned_captain=captain_name).values_list("ship_id", flat=True)
		alerts_qs = alerts_qs.filter(ship_id__in=captain_ships)
		if ship_id:
			alerts_qs = alerts_qs.filter(ship_id=ship_id)
	elif role == "command":
		# Command has full access to all alerts
		if ship_id:
			alerts_qs = alerts_qs.filter(ship_id=ship_id)
	else:
		# Default: full access if no role specified
		if ship_id:
			alerts_qs = alerts_qs.filter(ship_id=ship_id)
	
	alerts_data = list(
		alerts_qs.order_by("-created_at")
		.values(
			"id",
			"alert_type",
			"severity",
			"message",
			"ship_id",
			"zone_id",
			"details",
			"created_at",
		)
	)[:50]
	for alert in alerts_data:
		alert["created_at"] = alert["created_at"].isoformat()
	return JsonResponse({"alerts": alerts_data})


def playback(request):
	role = request.GET.get("role")
	captain_name = request.GET.get("captain_name")
	ship_id = request.GET.get("ship_id")
	
	if not ship_id:
		return JsonResponse({"error": "missing_ship_id"}, status=400)
	
	# Role-based access control
	if role == "captain":
		if not captain_name:
			return JsonResponse({"error": "missing_captain_name"}, status=400)
		# Verify captain can access this ship
		try:
			ship = Ship.objects.get(ship_id=ship_id)
			if ship.assigned_captain != captain_name:
				return JsonResponse({"error": "unauthorized"}, status=403)
		except Ship.DoesNotExist:
			return JsonResponse({"error": "ship_not_found"}, status=404)
	elif role == "command":
		# Command has full access
		pass
	else:
		# Default: allow if no role specified
		pass

	cutoff = timezone.now() - timedelta(hours=1)
	snapshots = list(
		ShipSnapshot.objects.filter(ship_id=ship_id, created_at__gte=cutoff)
		.order_by("created_at")
		.values(
			"latitude",
			"longitude",
			"speed",
			"heading",
			"fuel",
			"status",
			"created_at",
		)
	)
	for snapshot in snapshots:
		snapshot["created_at"] = snapshot["created_at"].isoformat()
	return JsonResponse({"ship_id": ship_id, "snapshots": snapshots})


@csrf_exempt
def distress(request):
	if request.method != "POST":
		return JsonResponse({"error": "method_not_allowed"}, status=405)

	payload = json.loads(request.body or "{}")
	ship_id = payload.get("ship_id")
	message = payload.get("message", "")
	if not ship_id or not message:
		return JsonResponse({"error": "missing_fields"}, status=400)

	try:
		ship = Ship.objects.get(ship_id=ship_id)
	except Ship.DoesNotExist:
		return JsonResponse({"error": "ship_not_found"}, status=404)

	parsed = parse_distress(message)
	alert = create_distress_alert(ship, parsed, message)
	broadcast_alerts()
	return JsonResponse({"alert_id": alert.id, "parsed": parsed})


@csrf_exempt
def distress_resolve(request):
	if request.method != "POST":
		return JsonResponse({"error": "method_not_allowed"}, status=405)

	payload = json.loads(request.body or "{}")
	ship_id = payload.get("ship_id")
	if not ship_id:
		return JsonResponse({"error": "missing_fields"}, status=400)

	try:
		ship = Ship.objects.get(ship_id=ship_id)
	except Ship.DoesNotExist:
		return JsonResponse({"error": "ship_not_found"}, status=404)

	if ship.status in {"distress", "stopped"}:
		ship.status = "normal"
		if ship.speed == 0:
			ship.speed = 12
			ship.save(update_fields=["status", "speed"])
		else:
			ship.save(update_fields=["status"])

	Alert.objects.filter(alert_type="distress", ship=ship, active=True).update(
		active=False
	)
	broadcast_alerts()
	return JsonResponse({"resolved": True, "ship_id": ship.ship_id})


def health(request):
	return JsonResponse({"status": "ok", "message": "Fleet API running."})
