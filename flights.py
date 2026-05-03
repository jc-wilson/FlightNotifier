import requests
import trajectory_calculator

# tm = TokenManager.from_json_file("credentials.json")
# api = OpenSkyApi(token_manager=tm)

def check_flights(x, y):
    flights = requests.get(f"https://api.airplanes.live/v2/point/{x}/{y}/50").json()

    for flight in flights["ac"]:
        if flight.get("track") is not None and flight.get("lat") is not None and flight.get("lon") is not None and flight.get("gs") is not None:
            if trajectory_calculator.calculate_trajectory(
                target_x=x,
                target_y=y,
                target_radius_miles=6,
                x=flight["lat"],
                y=flight["lon"],
                track=flight["track"],
                speed=flight["gs"],
                lookahead_minutes=3,
            ):
                return {
                    "ICAO24": flight.get("hex", ""),
                    "callsign": flight.get("flight", ""),
                    "registration": flight.get("r", ""),
                    "type": flight.get("t", ""),
                    "desc": flight.get("desc", ""),
                    "operator": flight.get("ownOp", ""),
                    "altitude": flight.get("alt_baro", ""),
                    "knots": flight.get("gs", ""),
                    "vert_speed": flight.get("baro_rate", ""),
                    "squawk": flight.get("squawk", ""),
                    "lat_lon": f"{flight.get('lat', '')}, {flight.get('lon', '')}",
                }

    return False