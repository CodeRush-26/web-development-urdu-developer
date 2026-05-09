from django.contrib import admin

from fleet.models import Alert, Port, RestrictedZone, Ship, ShipSnapshot


@admin.register(Ship)
class ShipAdmin(admin.ModelAdmin):
	list_display = ["ship_id", "name", "destination", "status", "fuel", "assigned_captain"]
	list_editable = ["assigned_captain"]
	search_fields = ["ship_id", "name", "assigned_captain"]
	list_filter = ["status"]
	fieldsets = (
		("Ship Info", {"fields": ("ship_id", "name", "destination")}),
		("Position", {"fields": ("latitude", "longitude")}),
		("Navigation", {"fields": ("heading", "speed")}),
		("Status", {"fields": ("status", "fuel")}),
		("Cargo & Captain", {"fields": ("cargo", "assigned_captain")}),
	)


@admin.register(Port)
class PortAdmin(admin.ModelAdmin):
	list_display = ["code", "name", "latitude", "longitude"]
	search_fields = ["code", "name"]


@admin.register(RestrictedZone)
class RestrictedZoneAdmin(admin.ModelAdmin):
	list_display = ["id", "name", "created_at"]
	search_fields = ["name"]
	list_filter = ["created_at"]


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
	list_display = ["id", "alert_type", "severity", "ship", "created_at", "active"]
	list_filter = ["alert_type", "severity", "active", "created_at"]
	search_fields = ["ship__ship_id", "message"]
	readonly_fields = ["created_at", "acknowledged_at"]


@admin.register(ShipSnapshot)
class ShipSnapshotAdmin(admin.ModelAdmin):
	list_display = ["id", "ship", "speed", "fuel", "created_at"]
	list_filter = ["ship", "created_at"]
	search_fields = ["ship__ship_id"]
	readonly_fields = ["created_at"]
