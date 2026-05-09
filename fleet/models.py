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
