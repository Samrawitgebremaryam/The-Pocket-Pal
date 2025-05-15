import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, filename='spot_finder.log')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

# Mock results as fallback
MOCK_RESULTS = {
    "addis ababa_quick meals": """
    BM African Restaurant, Addis Ababa, Ethiopia
    Portico Restaurant, Addis Ababa, Ethiopia
    Miki, Addis Ababa, Ethiopia
    9-Ja, Addis Ababa, Ethiopia
    Mistir Buna Ena Migeb, Addis Ababa, Ethiopia
    """
}

def query_geoapify_places(destination, need):
    if not destination.strip() or not need.strip():
        logger.error("Invalid destination or need provided.")
        return "Please provide a valid city and need (e.g., restaurants)."

    destination = destination.strip().title()
    if destination.lower() in ["addis abeba", "addis ababa"]:
        destination = "Addis Ababa"

    need_mapping = {
        "quick meals": "catering.restaurant",
        "restaurants": "catering.restaurant",
        "cafes": "catering.cafe",
        "hotels": "accommodation.hotel",
        "attractions": "tourism.sights"
    }
    place_category = need_mapping.get(need.lower(), "catering.restaurant")

    if not GEOAPIFY_API_KEY:
        logger.warning("Geoapify API key not set. Using mock results.")
        return MOCK_RESULTS.get(f"{destination.lower()}_{need.lower()}", f"No {need} found in {destination}.")

    try:
        # Geoapify Places API request
        url = "https://api.geoapify.com/v2/places"
        params = {
            "apiKey": GEOAPIFY_API_KEY,
            "categories": place_category,
            "filter": f"circle:38.74,9.03,5000",  # Addis Ababa, 5km radius
            "limit": 5,
            "lang": "en"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        places = response.json().get("features", [])

        results = []
        for place in places[:5]:
            name = place["properties"].get("name", "Unknown place")
            address = place["properties"].get("formatted", "Addis Ababa, Ethiopia")
            results.append(f"{name}, {address}")
        if not results:
            logger.info(f"No {place_category}s found in {destination} via Geoapify.")
            return MOCK_RESULTS.get(f"{destination.lower()}_{need.lower()}", f"No {need} found in {destination}.")
        logger.info(f"Found {len(results)} places for {place_category} in {destination}.")
        return "\n".join(results)
    except Exception as e:
        logger.error(f"Geoapify Places query failed: {e}")
        return MOCK_RESULTS.get(f"{destination.lower()}_{need.lower()}", f"No {need} found in {destination}.")

@app.route("/spot_finder", methods=["POST"])
def spot_finder():
    try:
        data = request.get_json()
        if not data or "destination" not in data or "need" not in data:
            logger.error("Invalid or missing JSON payload.")
            return jsonify({"error": "Destination and need are required in JSON payload"}), 400

        destination = data.get("destination")
        need = data.get("need")
        recommendation = query_geoapify_places(destination, need)
        return jsonify({"recommendation": recommendation})
    except Exception as e:
        logger.error(f"Unexpected error in spot_finder: {e}")
        return jsonify({"error": "Something went wrong"}), 500

if __name__ == "__main__":
    logger.info("Starting Spot Finder on port 5002...")
    app.run(host="0.0.0.0", port=5002, debug=True)