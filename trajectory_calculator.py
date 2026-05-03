import math

EARTH_RADIUS_MILES = 3958.8
KNOTS_TO_MPH = 1.15078

def destination_point(lat, lon, bearing_deg, distance_miles):
    bearing = math.radians(bearing_deg)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    angular_distance = distance_miles / EARTH_RADIUS_MILES

    lat2 = math.asin(
        math.sin(lat1) * math.cos(angular_distance)
        + math.cos(lat1) * math.sin(angular_distance) * math.cos(bearing)
    )

    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(angular_distance) * math.cos(lat1),
        math.cos(angular_distance) - math.sin(lat1) * math.sin(lat2)
    )

    return math.degrees(lat2), math.degrees(lon2)

def latlon_to_local_miles(lat, lon, origin_lat, origin_lon):
    """
    Converts lat/lon to local x/y miles around origin.
    Good enough for small radii like 10-100 miles.
    """
    lat_miles = (lat - origin_lat) * 69.0
    lon_miles = (lon - origin_lon) * 69.0 * math.cos(math.radians(origin_lat))
    return lon_miles, lat_miles  # x=east/west, y=north/south

def calculate_trajectory(
    target_x,
    target_y,
    target_radius_miles,
    x,
    y,
    track,
    speed,
    lookahead_minutes=3,
):
    """
    x, y: aircraft lat/lon
    target_x, target_y: target lat/lon
    speed: knots
    track: degrees, 0=north, 90=east

    Returns True if aircraft is projected to pass within target_radius_miles
    of the target within lookahead_minutes.
    """

    aircraft_lat = x
    aircraft_lon = y
    target_lat = target_x
    target_lon = target_y

    if track is None or speed is None or speed <= 0:
        return False

    speed_mph = speed * KNOTS_TO_MPH
    distance_miles = speed_mph * (lookahead_minutes / 60)

    future_lat, future_lon = destination_point(
        aircraft_lat,
        aircraft_lon,
        track,
        distance_miles
    )

    # Convert aircraft, future point, and target into local flat miles
    # using the target as origin.
    aircraft_px, aircraft_py = latlon_to_local_miles(
        aircraft_lat,
        aircraft_lon,
        target_lat,
        target_lon
    )
    future_px, future_py = latlon_to_local_miles(
        future_lat,
        future_lon,
        target_lat,
        target_lon
    )

    # Target is origin in this local system.
    target_px, target_py = 0, 0

    segment_dx = future_px - aircraft_px
    segment_dy = future_py - aircraft_py

    segment_len_sq = segment_dx ** 2 + segment_dy ** 2
    if segment_len_sq == 0:
        return False

    # Find closest point on aircraft path segment to target.
    t = (
        ((target_px - aircraft_px) * segment_dx)
        + ((target_py - aircraft_py) * segment_dy)
    ) / segment_len_sq

    # Clamp to segment: current position -> projected future position.
    t = max(0, min(1, t))

    closest_x = aircraft_px + t * segment_dx
    closest_y = aircraft_py + t * segment_dy

    distance_to_target = math.hypot(
        closest_x - target_px,
        closest_y - target_py
    )

    return distance_to_target <= target_radius_miles
