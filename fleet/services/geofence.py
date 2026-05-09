from __future__ import annotations

import math


def point_in_polygon(point: tuple[float, float], polygon: list[list[float]]) -> bool:
    if len(polygon) < 3:
        return False

    lat, lon = point
    x = lon
    y = lat
    inside = False
    j = len(polygon) - 1
    for i, (lat_i, lon_i) in enumerate(polygon):
        lat_j, lon_j = polygon[j]
        x_i = lon_i
        y_i = lat_i
        x_j = lon_j
        y_j = lat_j
        intersects = ((y_i > y) != (y_j > y)) and (
            x < (x_j - x_i) * (y - y_i) / (y_j - y_i + 1e-12) + x_i
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def polygon_centroid(polygon: list[list[float]]) -> tuple[float, float]:
    if not polygon:
        return 0.0, 0.0

    lat_sum = 0.0
    lon_sum = 0.0
    for lat, lon in polygon:
        lat_sum += lat
        lon_sum += lon

    count = len(polygon)
    return lat_sum / count, lon_sum / count


def bearing_from_to(source: tuple[float, float], target: tuple[float, float]) -> int:
    lat1, lon1 = map(math.radians, source)
    lat2, lon2 = map(math.radians, target)
    delta_lon = lon2 - lon1

    y = math.sin(delta_lon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    bearing = (math.degrees(math.atan2(y, x)) + 360) % 360
    return int(round(bearing))
