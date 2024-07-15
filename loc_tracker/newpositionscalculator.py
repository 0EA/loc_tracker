import math
from geopy.distance import geodesic as GD

def calculate_bearing(lon1, lat1, lon2, lat2):
    delta_lon = math.radians(lon1 - lon2)
    lat1_rad = math.radians(lat2)
    lat2_rad = math.radians(lat1)

    y = math.sin(delta_lon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)

    bearing = math.atan2(y, x)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360

    return bearing

def calculate_rotation_angle(side1, side2, side3):
    if side1 != 0 and side2 != 0 and side3 != 0:
        try:
            return math.degrees(math.acos((-(side3**2) + (side1**2) + (side2**2)) / ((2 * side1 * side2))))
        except Exception as e:
            return 0
    else:
        return 0


def calculate_new_position(lat, lon, bearing, distance):
    new_position = GD(kilometers=distance).destination((lat, lon), bearing)

    return new_position.latitude, new_position.longitude