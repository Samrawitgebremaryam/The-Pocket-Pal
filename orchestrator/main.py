from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import os
import requests
from shared.config import AGENT2_URL, AGENT3_URL

app = Flask(__name__)

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
except Exception as e:
    print(f"Gemini initialization failed: {e}. Using mock responses.")
    GEMINI_AVAILABLE = False

def parse_prompt(prompt):
    """Parse the user prompt using Gemini or keyword matching."""
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
    response = model.generate_content(gemini_prompt)
    try:
        parsed = eval(response.text.strip("```json\n").strip("```"))
        return (
            parsed.get("destination"),
            parsed.get("need"),
            parsed.get("phrase"),
            parsed.get("general_query")
        )
    except:
        # Fallback to mock parsing if Gemini fails
        return None, None, None, prompt

@app.route("/orchestrator", methods=["POST"])
def orchestrator():
    data = request.get_json()
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Parse the prompt
    destination, need, phrase, general_query = parse_prompt(prompt)
    output = []

    # Handle spot recommendation if destination and need are provided
    if destination and need:
        try:
            response = requests.post(
                AGENT2_URL,
                json={"destination": destination, "need": need},
                timeout=5
            )
            if response.status_code == 200:
                output.append(response.json().get("recommendation"))
            else:
                output.append(f"Error fetching recommendation: {response.text}")
        except requests.RequestException as e:
            output.append(f"Error connecting to Spot Finder: {e}")

    # Handle translation if phrase is provided
    if phrase:
        try:
            response = requests.post(
                AGENT3_URL,
                json={"phrase": phrase, "destination": destination or "unknown"},
                timeout=5
            )
            if response.status_code == 200:
                output.append(response.json().get("translation"))
            else:
                output.append(f"Error fetching translation: {response.text}")
        except requests.RequestException as e:
            output.append(f"Error connecting to Phrase Translator: {e}")

    # Handle general query if no specific tasks or as fallback
    if not (destination and need) and not phrase and general_query:
        if GEMINI_AVAILABLE:
            try:
                response = model.generate_content(general_query)
                output.append(response.text)
            except Exception as e:
                output.append(MOCK_RESPONSES.get(general_query, "Sorry, I can’t answer that. Try a specific travel query."))
        else:
            output.append(MOCK_RESPONSES.get(general_query, "Sorry, I can’t answer that. Try a specific travel query."))

    return jsonify({"output": "\n\n".join(output)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)