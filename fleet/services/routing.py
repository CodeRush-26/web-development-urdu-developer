from fleet.services.geofence import bearing_from_to, polygon_centroid


def compute_reroute_heading(ship_lat: float, ship_lon: float, zone_polygon: list[list[float]]) -> int:
    centroid = polygon_centroid(zone_polygon)
    # Move outward from the zone centroid to exit quickly.
    return bearing_from_to(centroid, (ship_lat, ship_lon))
