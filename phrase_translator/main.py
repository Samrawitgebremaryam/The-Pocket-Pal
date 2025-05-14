import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request, jsonify
from googletrans import Translator, LANGUAGES
import pycountry
import logging

app = Flask(__name__)
translator = Translator()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_language_from_destination(destination):
    """Map destination to its primary language."""
    if not destination or not destination.strip():
        logger.warning("No valid destination provided, defaulting to English.")
        return "en"

    # Simple mapping of cities/countries to language codes
    destination_language_map = {
        "barcelona": "es",
        "spain": "es",
        "tokyo": "ja",
        "japan": "ja",
        "paris": "fr",
        "france": "fr",
        "unknown": "en"
    }

    # Normalize destination
    destination = destination.lower().strip()

    # Check if destination is a country
    try:
        country = pycountry.countries.search_fuzzy(destination)[0]
        country_language_map = {
            "Spain": "es",
            "Japan": "ja",
            "France": "fr"
        }
        lang = country_language_map.get(country.name, "en")
        logger.info(f"Mapped destination {destination} to language {lang}.")
        return lang
    except LookupError:
        lang = destination_language_map.get(destination, "en")
        logger.info(f"Mapped destination {destination} to language {lang}.")
        return lang

@app.route("/phrase_translator", methods=["POST"])
def phrase_translator():
    try:
        data = request.get_json()
        if not data or "phrase" not in data:
            logger.error("Invalid or missing JSON payload.")
            return jsonify({"error": "Phrase is required in JSON payload"}), 400

        phrase = data.get("phrase")
        destination = data.get("destination", "unknown")

        if not phrase.strip():
            logger.error("Empty phrase provided.")
            return jsonify({"error": "Phrase cannot be empty"}), 400

        # Get target language
        target_lang = get_language_from_destination(destination)

        try:
            # Translate the phrase
            translation = translator.translate(phrase, dest=target_lang)
            result = f"'{phrase}' in {LANGUAGES.get(target_lang, 'unknown')} ({target_lang}): {translation.text}"
            logger.info(f"Translated '{phrase}' to {target_lang}: {translation.text}")
            return jsonify({"translation": result})
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return jsonify({"error": "Unable to translate at this time"}), 500
    except Exception as e:
        logger.error(f"Unexpected error in phrase_translator: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)