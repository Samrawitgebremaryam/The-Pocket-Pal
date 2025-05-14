import streamlit as st
import requests
from shared.config import AGENT1_URL
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Streamlit app configuration
st.set_page_config(page_title="The Traveler’s Pocket Pal", layout="wide")

# Header and styling
st.markdown("""
    <h1 style='font-size: 2.5em;'>✈️ <span style='color:#ffffff;'>The Traveler’s Pocket Pal</span></h1>
    <p style='font-size: 1.1em;'>Your AI-powered travel companion! Enter a prompt to get spot recommendations, translations, or general travel info.</p>

    <style>
        /* Custom bottom input box */
        div[data-testid="stTextInput"] {
            position: fixed;
            bottom: 1.5rem;
            left: 26%;
            width: 65%;
            z-index: 9999;
            background: transparent;
        }

        div[data-testid="stTextInput"] input {
            width: 100%;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            border-radius: 10px;
            border: 1px solid #444;
            background-color: #262730;
            color: white;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        div[data-testid="stTextInput"] input::placeholder {
            color: #ccc;
            opacity: 0.8;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar for additional options (optional for future enhancements)
with st.sidebar:
    st.header("Travel Options")
    st.markdown("Configure your preferences (optional).")
    learning_mode = st.checkbox("Learning Mode")
    if learning_mode:
        st.markdown("**Tip**: Enter a prompt like 'Find quick meals in Barcelona and translate \"Can I have this to go?\"' or 'What’s the weather in Tokyo?'")

# Single input field
user_prompt = st.text_input("", placeholder="Enter your travel prompt (e.g., Find quick meals in Barcelona and translate 'Can I have this to go?')", key="user_prompt")

# Handle submission
if user_prompt.strip():
    # Send prompt to Agent 1
    payload = {"prompt": user_prompt.strip()}
    try:
        response = requests.post(AGENT1_URL, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            st.markdown("### 🌍 Your Travel Response")
            st.markdown(result.get("output", "No response received."), unsafe_allow_html=True)
        else:
            st.error(f"Error from Agent 1: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        st.error(f"Failed to connect to Agent 1: {e}")

# Footer
st.markdown("---")
st.markdown("Powered by A2A Protocol and MCP Tools (OpenStreetMap Nominatim, googletrans)")