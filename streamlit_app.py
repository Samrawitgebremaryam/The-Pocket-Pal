import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import streamlit as st
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import logging
from shared.config import AGENT2_URL, AGENT3_URL
from googletrans import LANGUAGES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Mock responses for general queries
MOCK_RESPONSES = {
    "what’s the weather in addis ababa?": "In Addis Ababa, May is typically warm with temperatures around 20-25°C and occasional rain.",
    "what are some local customs in tokyo?": "In Tokyo, it’s customary to bow when greeting and remove shoes before entering homes.",
}

# Initialize Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    GEMINI_AVAILABLE = True
    logger.info("Gemini API initialized successfully.")
except Exception as e:
    logger.warning(f"Gemini initialization failed: {e}. Using mock responses.")
    GEMINI_AVAILABLE = False

# Streamlit app configuration
st.set_page_config(page_title="The Traveler’s Pocket Pal", layout="wide")

# Header and dark mode styling
st.markdown("""
    <style>
        /* Dark mode app background */
        .stApp {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        /* Header styling */
        .header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .header h1 {
            font-size: 2.5em;
            font-family: 'Arial', sans-serif;
            color: #ffffff;
            background-color: #262730;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        .header p {
            font-size: 1.1em;
            color: #cccccc;
            font-style: italic;
        }
        /* Sidebar styling */
        .css-1lcbmhc, .css-1d391kg {
            background-color: #262730;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        .sidebar .sidebar-content {
            color: #ffffff;
        }
        /* Input field styling (initial dark mode) */
        div[data-testid="stTextInput"] input {
            width: 100%;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            border-radius: 10px;
            border: 1px solid #444;
            background-color: #262730;
            color: white;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: #1e90ff;
            box-shadow: 0 0 8px rgba(30, 144, 255, 0.5);
        }
        div[data-testid="stTextInput"] input::placeholder {
            color: #ccc;
            opacity: 0.8;
            font-style: italic;
        }
        /* Selectbox styling */
        .stSelectbox select {
            background-color: #262730;
            color: white;
            border-radius: 10px;
            padding: 0.5rem;
            border: 1px solid #444;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
        /* Submit button (icon) */
        .submit-button {
            background: none;
            border: none;
            cursor: pointer;
            margin-left: 0.5rem;
            vertical-align: middle;
            color: #1e90ff;
            font-size: 1.5rem;
        }
        .submit-button:hover {
            transform: scale(1.2);
            transition: transform 0.2s ease;
            color: #ff4500;
        }
        /* Response area */
        .response-box {
            background-color: #262730;
            padding: 1.5rem;
            border-radius: 10px;
            margin-top: 1rem;
            color: #ffffff;
            font-size: 1.1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        /* Subheader styling */
        h2 {
            color: #1e90ff;
            font-size: 1.8em;
        }
    </style>
    <div class="header">
        <h1>✈️ The Traveler’s Pocket Pal</h1>
        <p>Your AI-powered travel companion! Choose a task and enter your request.</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar with task selector
with st.sidebar:
    st.markdown("<h2 style='color: #ffffff;'>Travel Options</h2>", unsafe_allow_html=True)
    learning_mode = st.checkbox("Learning Mode", help="Get tips for using the app!")
    if learning_mode:
        st.markdown("""
            **Tips**:
            - **Translate**: Pick languages and type a phrase like 'Hello!'.
            - **Spot Finder**: Enter a city and what you need, like 'quick meals'.
            - **Random**: Ask anything, like 'What’s the vibe in Addis Ababa?'.
        """)
    st.markdown("<h3 style='color: #ffffff;'>Choose Your Task</h3>", unsafe_allow_html=True)
    task = st.selectbox("", ["random", "translate", "spot_finder"], key="task", help="Select what you want to do!")

# Initialize session state
if "submit_clicked" not in st.session_state:
    st.session_state.submit_clicked = False

# Input fields based on task
if task == "translate":
    st.subheader("🌍 Translate a Phrase")
    col1, col2 = st.columns([5, 1])
    with col1:
        source_lang = st.selectbox("From Language:", list(LANGUAGES.values()), index=list(LANGUAGES.values()).index("english"))
        target_lang = st.selectbox("To Language:", list(LANGUAGES.values()), index=list(LANGUAGES.values()).index("amharic"))
        phrase = st.text_input("", placeholder="Type your phrase, like 'My name is Samri'", key="phrase")
    with col2:
        st.markdown("<div style='margin-top: 2.5rem;'></div>", unsafe_allow_html=True)
        if st.button("✈️", key="translate_submit", help="Submit translation"):
            st.session_state.submit_clicked = True
    source_lang_code = [k for k, v in LANGUAGES.items() if v == source_lang][0]
    target_lang_code = [k for k, v in LANGUAGES.items() if v == target_lang][0]
elif task == "spot_finder":
    st.subheader("🍽️ Find Places")
    col1, col2 = st.columns([5, 1])
    with col1:
        destination = st.text_input("", placeholder="Where are you headed? e.g., Addis Ababa", key="destination")
        need = st.text_input("", placeholder="What do you need? e.g., quick meals", key="need")
    with col2:
        st.markdown("<div style='margin-top: 2.5rem;'></div>", unsafe_allow_html=True)
        if st.button("✈️", key="spot_submit", help="Find places"):
            st.session_state.submit_clicked = True
else:  # random
    st.subheader("❓ Ask Anything")
    col1, col2 = st.columns([5, 1])
    with col1:
        query = st.text_input("", placeholder="Curious? Ask like 'What’s the weather in Addis Ababa?'", key="query")
    with col2:
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        if st.button("✈️", key="random_submit", help="Get your answer"):
            st.session_state.submit_clicked = True

# Process submission
if st.session_state.submit_clicked:
    output = []
    if task == "translate" and phrase.strip():
        try:
            response = requests.post(
                AGENT3_URL,
                json={"phrase": phrase, "source_lang": source_lang_code, "target_lang": target_lang_code},
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
    elif task == "spot_finder" and destination.strip() and need.strip():
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
    elif task == "random" and query.strip():
        if GEMINI_AVAILABLE:
            try:
                response = model.generate_content(query)
                output.append(response.text)
            except Exception as e:
                logger.error(f"Gemini query failed: {e}")
                output.append(MOCK_RESPONSES.get(query.lower(), "Sorry, I can’t answer that. Try a specific travel query."))
        else:
            output.append(MOCK_RESPONSES.get(query.lower(), "Sorry, I can’t answer that. Try a specific travel query."))

    # Display results
    if output:
        st.markdown("<div class='response-box'>", unsafe_allow_html=True)
        st.markdown("### 🌍 Your Travel Response")
        st.markdown("\n\n".join(output), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("Please fill in all required fields correctly.")
    st.session_state.submit_clicked = False

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #cccccc;'>Powered by A2A Protocol and MCP Tools (OpenStreetMap Nominatim, googletrans)</p>", unsafe_allow_html=True)