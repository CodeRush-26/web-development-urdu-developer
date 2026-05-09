from django.db import models


class Port(models.Model):
	code = models.CharField(max_length=10, primary_key=True)
	name = models.CharField(max_length=100)
	latitude = models.FloatField()
	longitude = models.FloatField()

	def __str__(self) -> str:
		return f"{self.code} - {self.name}"


class NavigableWater(models.Model):
	name = models.CharField(max_length=100, default="default")
	polygon = models.JSONField()

	def __str__(self) -> str:
		return self.name


class Ship(models.Model):
	ship_id = models.CharField(max_length=10, primary_key=True)
	name = models.CharField(max_length=100)
	latitude = models.FloatField()
	longitude = models.FloatField()
	speed = models.FloatField()
	heading = models.IntegerField()
	destination = models.ForeignKey(Port, on_delete=models.PROTECT)
	fuel = models.FloatField()
	cargo = models.CharField(max_length=100)
	status = models.CharField(max_length=50)

	def __str__(self) -> str:
		return f"{self.ship_id} - {self.name}"


class RestrictedZone(models.Model):
	name = models.CharField(max_length=100)
	polygon = models.JSONField()
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return self.name


class Alert(models.Model):
	ALERT_TYPES = (
		("geofence", "geofence"),
		("proximity", "proximity"),
		("distress", "distress"),
		("system", "system"),
	)
	SEVERITIES = (
		("info", "info"),
		("warning", "warning"),
		("critical", "critical"),
	)
	alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
	severity = models.CharField(max_length=20, choices=SEVERITIES, default="warning")
	message = models.TextField()
	details = models.JSONField(default=dict, blank=True)
	ship = models.ForeignKey(Ship, on_delete=models.CASCADE)
	zone = models.ForeignKey(RestrictedZone, on_delete=models.SET_NULL, null=True, blank=True)
	active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	acknowledged_at = models.DateTimeField(null=True, blank=True)

	def __str__(self) -> str:
		return f"{self.alert_type} - {self.ship.ship_id}"


class SimulationState(models.Model):
	key = models.CharField(max_length=50, primary_key=True)
	last_tick = models.DateTimeField(null=True, blank=True)

	def __str__(self) -> str:
		return self.key
