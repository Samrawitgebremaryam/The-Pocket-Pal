import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request, jsonify
from googletrans import Translator, LANGUAGES
import logging

app = Flask(__name__)
translator = Translator()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/phrase_translator", methods=["POST"])
def phrase_translator():
    try:
        data = request.get_json()
        if not data or "phrase" not in data or "source_lang" not in data or "target_lang" not in data:
            logger.error("Invalid or missing JSON payload.")
            return jsonify({"error": "Phrase, source_lang, and target_lang are required in JSON payload"}), 400

        phrase = data.get("phrase")
        source_lang = data.get("source_lang")
        target_lang = data.get("target_lang")
        if not phrase.strip():
            logger.error("Empty phrase provided.")
            return jsonify({"error": "Phrase cannot be empty"}), 400

        try:
            translation = translator.translate(phrase, src=source_lang, dest=target_lang)
            result = f"'{phrase}' from {LANGUAGES.get(source_lang, 'unknown')} ({source_lang}) to {LANGUAGES.get(target_lang, 'unknown')} ({target_lang}): {translation.text}"
            logger.info(f"Translated '{phrase}' from {source_lang} to {target_lang}: {translation.text}")
            return jsonify({"translation": result})
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return jsonify({"error": "Unable to translate at this time"}), 500
    except Exception as e:
        logger.error(f"Unexpected error in phrase_translator: {e}")
        return jsonify({"error": "Something went wrong"}), 500

if __name__ == "__main__":
    logger.info("Starting Phrase Translator on port 5003...")
    app.run(host="0.0.0.0", port=5003, debug=True)