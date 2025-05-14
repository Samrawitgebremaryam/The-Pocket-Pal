import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import requests
import json
import logging
from shared.config import AGENT2_URL, AGENT3_URL

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Mock responses for general queries if Gemini key is invalid
MOCK_RESPONSES = {
    "What’s the weather in Barcelona?": "The weather in Barcelona is typically sunny in May, with temperatures around 20°C.",
    "What are some local customs in Tokyo?": "In Tokyo, it’s customary to bow when greeting and remove shoes before entering homes."
}

# Initialize Gemini if key is valid
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    GEMINI_AVAILABLE = True
    logger.info("Gemini API initialized successfully.")
except Exception as e:
    logger.warning(f"Gemini initialization failed: {e}. Using mock responses.")
    GEMINI_AVAILABLE = False

def parse_prompt(prompt):
    """Parse the user prompt using Gemini or keyword matching."""
    if not prompt.strip():
        logger.error("Empty prompt provided.")
        return None, None, None, None

    if not GEMINI_AVAILABLE:
        # Mock parsing for testing
        destination = None
        need = None
        phrase = None
        general_query = prompt.lower()

        if "find" in general_query and "in" in general_query:
            parts = general_query.split(" in ")
            if len(parts) > 1:
                need = parts[0].replace("find", "").strip()
                destination = parts[1].strip()
        if "translate" in general_query:
            phrase_start = general_query.find("translate") + len("translate")
            phrase = general_query[phrase_start:].strip().strip("'\"")
        logger.info(f"Mock parsing result: destination={destination}, need={need}, phrase={phrase}, general_query={general_query}")
        return destination, need, phrase, general_query

    # Use Gemini to parse the prompt
    gemini_prompt = (
        f"Parse the following user prompt into four components: "
        f"destination (city and country), need (e.g., finding quick meals), "
        f"phrase to translate, and general query (if no specific task). "
        f"Return as JSON with fields: destination, need, phrase, general_query. "
        f"If a component is not present, return null for that field. "
        f"Prompt: '{prompt}'"
    )
    try:
        response = model.generate_content(gemini_prompt)
        parsed_text = response.text.strip("```json\n").strip("```")
        parsed = json.loads(parsed_text)
        logger.info(f"Gemini parsing result: {parsed}")
        return (
            parsed.get("destination"),
            parsed.get("need"),
            parsed.get("phrase"),
            parsed.get("general_query")
        )
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Gemini parsing failed: {e}. Falling back to mock parsing.")
        return None, None, None, prompt

@app.route("/orchestrator", methods=["POST"])
def orchestrator():
    try:
        data = request.get_json()
        if not data or "prompt" not in data:
            logger.error("Invalid or missing JSON payload.")
            return jsonify({"error": "Invalid or missing prompt in JSON payload"}), 400

        prompt = data.get("prompt")
        if not isinstance(prompt, str):
            logger.error("Prompt must be a string.")
            return jsonify({"error": "Prompt must be a string"}), 400

        # Parse the prompt
        destination, need, phrase, general_query = parse_prompt(prompt)
        output = []

        # Handle spot recommendation
        if destination and need:
            try:
                response = requests.post(
                    AGENT2_URL,
                    json={"destination": destination, "need": need},
                    timeout=5
                )
                if response.status_code == 200:
                    output.append(response.json().get("recommendation", "No recommendation received."))
                else:
                    logger.warning(f"Agent 2 error: {response.status_code} - {response.text}")
                    output.append(f"Error fetching recommendation: {response.text}")
            except requests.RequestException as e:
                logger.error(f"Agent 2 connection failed: {e}")
                output.append("Unable to fetch recommendations at this time.")

        # Handle translation
        if phrase:
            try:
                response = requests.post(
                    AGENT3_URL,
                    json={"phrase": phrase, "destination": destination or "unknown"},
                    timeout=5
                )
                if response.status_code == 200:
                    output.append(response.json().get("translation", "No translation received."))
                else:
                    logger.warning(f"Agent 3 error: {response.status_code} - {response.text}")
                    output.append(f"Error fetching translation: {response.text}")
            except requests.RequestException as e:
                logger.error(f"Agent 3 connection failed: {e}")
                output.append("Unable to fetch translation at this time.")

        # Handle general query
        if not output and general_query:
            if GEMINI_AVAILABLE:
                try:
                    response = model.generate_content(general_query)
                    output.append(response.text)
                except Exception as e:
                    logger.error(f"Gemini query failed: {e}")
                    output.append(MOCK_RESPONSES.get(general_query.lower(), "Sorry, I can’t answer that. Try a specific travel query."))
            else:
                output.append(MOCK_RESPONSES.get(general_query.lower(), "Sorry, I can’t answer that. Try a specific travel query."))

        if not output:
            logger.warning("No valid tasks identified in prompt.")
            return jsonify({"error": "No valid tasks identified in prompt"}), 400

        return jsonify({"output": "\n\n".join(output)})
    except Exception as e:
        logger.error(f"Unexpected error in orchestrator: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)