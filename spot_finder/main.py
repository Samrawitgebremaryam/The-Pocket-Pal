import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request, jsonify
import requests
from shared.config import NOMINATIM_USER_AGENT
import time
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Nominatim API base URL
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def query_nominatim(destination, need):
    """Query Nominatim API for places matching destination and need."""
    if not destination.strip() or not need.strip():
        logger.error("Invalid destination or need provided.")
        return "Destination and need cannot be empty."

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
        "limit": 3
    }

    try:
        # Respect Nominatim's 1 request/second rate limit
        time.sleep(1)
        response = requests.get(NOMINATIM_URL, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            places = response.json()
            if not places:
                logger.info(f"No {place_type}s found in {destination}.")
                return f"No {place_type}s found in {destination}."
            results = [
                f"{place['display_name']} (Lat: {place['lat']}, Lon: {place['lon']})"
                for place in places
            ]
            logger.info(f"Found {len(results)} places for {query}.")
            return "\n".join(results)
        elif response.status_code == 429:
            logger.warning("Nominatim rate limit exceeded.")
            return "Rate limit exceeded. Please try again later."
        else:
            logger.warning(f"Nominatim error: {response.status_code} - {response.text}")
            return f"Error from Nominatim: {response.status_code}"
    except requests.RequestException as e:
        logger.error(f"Nominatim query failed: {e}")
        return "Unable to fetch recommendations at this time."

@app.route("/spot_finder", methods=["POST"])
def spot_finder():
    try:
        data = request.get_json()
        if not data or "destination" not in data or "need" not in data:
            logger.error("Invalid or missing JSON payload.")
            return jsonify({"error": "Destination and need are required in JSON payload"}), 400

        destination = data.get("destination")
        need = data.get("need")

        # Query Nominatim
        recommendation = query_nominatim(destination, need)
        return jsonify({"recommendation": recommendation})
    except Exception as e:
        logger.error(f"Unexpected error in spot_finder: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)