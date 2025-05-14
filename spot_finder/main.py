from flask import Flask, request, jsonify
import requests
from shared.config import NOMINATIM_USER_AGENT
import time

app = Flask(__name__)

# Nominatim API base URL
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def query_nominatim(destination, need):
    """Query Nominatim API for places matching destination and need."""
    # Map common needs to Nominatim tags
    need_mapping = {
        "quick meals": "restaurant",
        "restaurants": "restaurant",
        "cafes": "cafe",
        "hotels": "hotel",
        "attractions": "tourism"
    }
    place_type = need_mapping.get(need.lower(), "amenity")

    # Prepare query
    query = f"{place_type} {destination}"
    headers = {"User-Agent": NOMINATIM_USER_AGENT}
    params = {
        "q": query,
        "format": "json",
        "limit": 3  # Return up to 3 results
    }

    try:
        # Respect Nominatim's 1 request/second rate limit
        time.sleep(1)
        response = requests.get(NOMINATIM_URL, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            places = response.json()
            if not places:
                return f"No {place_type}s found in {destination}."
            results = [
                f"{place['display_name']} (Lat: {place['lat']}, Lon: {place['lon']})"
                for place in places
            ]
            return "\n".join(results)
        else:
            return f"Error from Nominatim: {response.status_code} - {response.text}"
    except requests.RequestException as e:
        return f"Error querying Nominatim: {e}"

@app.route("/spot_finder", methods=["POST"])
def spot_finder():
    data = request.get_json()
    destination = data.get("destination")
    need = data.get("need")

    if not destination or not need:
        return jsonify({"error": "Destination and need are required"}), 400

    # Query Nominatim
    recommendation = query_nominatim(destination, need)
    return jsonify({"recommendation": recommendation})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)