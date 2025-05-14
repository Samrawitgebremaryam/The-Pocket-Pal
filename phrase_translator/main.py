from flask import Flask, request, jsonify
from googletrans import Translator, LANGUAGES
import pycountry

app = Flask(__name__)
translator = Translator()

def get_language_from_destination(destination):
    """Map destination to its primary language."""
    # Simple mapping of cities/countries to language codes
    destination_language_map = {
        "barcelona": "es",  # Spanish
        "spain": "es",
        "tokyo": "ja",     # Japanese
        "japan": "ja",
        "paris": "fr",     # French
        "france": "fr",
        "unknown": "en"    # Default to English
    }

    # Normalize destination to lowercase
    destination = destination.lower().strip()

    # Check if destination is a country
    try:
        country = pycountry.countries.search_fuzzy(destination)[0]
        # Map country to language (simplified)
        country_language_map = {
            "Spain": "es",
            "Japan": "ja",
            "France": "fr"
        }
        return country_language_map.get(country.name, "en")
    except LookupError:
        # If not a country, try direct mapping
        return destination_language_map.get(destination, "en")

@app.route("/phrase_translator", methods=["POST"])
def phrase_translator():
    data = request.get_json()
    phrase = data.get("phrase")
    destination = data.get("destination", "unknown")

    if not phrase:
        return jsonify({"error": "Phrase is required"}), 400

    # Get target language
    target_lang = get_language_from_destination(destination)

    try:
        # Translate the phrase
        translation = translator.translate(phrase, dest=target_lang)
        result = f"'{phrase}' in {LANGUAGES.get(target_lang, 'unknown')} ({target_lang}): {translation.text}"
        return jsonify({"translation": result})
    except Exception as e:
        return jsonify({"error": f"Translation failed: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)