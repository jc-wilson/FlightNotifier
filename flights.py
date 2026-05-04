import requests
import trajectory_calculator

# tm = TokenManager.from_json_file("credentials.json")
# api = OpenSkyApi(token_manager=tm)

def check_flights(x, y, radius):
    response = requests.get(f"https://api.airplanes.live/v2/point/{x}/{y}/50").json()
    matching_flights = []

    for flight in response["ac"]:
        altitude = flight.get("alt_baro")

        if (
            flight.get("track") is not None
            and flight.get("lat") is not None
            and flight.get("lon") is not None
            and flight.get("gs") is not None
            and isinstance(altitude, (int, float))
        ):
            if trajectory_calculator.calculate_trajectory(
                target_x=x,
                target_y=y,
                target_radius_miles=radius,
                x=flight["lat"],
                y=flight["lon"],
                track=flight["track"],
                speed=flight["gs"],
                lookahead_minutes=3,
            ):
                matching_flights.append({
                    "callsign": flight.get("flight", "").strip() or "Unknown",
                    "registration": flight.get("r", ""),
                    "type": flight.get("t", ""),
                    "altitude": altitude,
                    "knots": flight.get("gs", ""),
                })

    return matching_flights
