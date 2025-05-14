import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = "AIzaSyC7b8PMlEcY4CybwpUNDoyHWT-yzUYGDlU"
if not api_key:
    st.error("API key not found. Please set the GEMINI_API_KEY environment variable.")
    st.stop()
genai.configure(api_key=api_key)

# Define writing styles
style_descriptions = {
    "Professional": "Formal, clear, and concise language suitable for business communications.",
    "Casual": "Informal and friendly tone, ideal for social media or personal blogs.",
    "Persuasive": "Engaging and convincing language aimed at influencing the reader's opinion or behavior.",
    "Empathetic": "Compassionate and understanding tone, appropriate for sensitive topics.",
    "Creative": "Imaginative and artistic language, perfect for storytelling or poetry."
}

audience_descriptions = {
    "General Public": "Content is tailored for a wide audience with varying backgrounds.",
    "Industry Professionals": "Language is technical and assumes familiarity with industry-specific terms.",
    "Academics": "Formal and scholarly tone, suitable for research papers or academic publications.",
    "Teens": "Casual and relatable language, appealing to a younger audience.",
    "Elderly": "Clear and respectful language, considering the preferences and needs of older readers."
}

prompt_type_descriptions = {
    "Zero-Shot": (
        "No examples are provided. The model generates a response based solely on the prompt's instructions."
    ),
    "Few-Shot": (
        "A few examples are provided to guide the model's response, improving format and accuracy."
    ),
    "Chain-of-Thought": (
        "The model reasons step-by-step before answering. Great for complex tasks."
    )
}

st.set_page_config(page_title="StyleCraft: Tailored Writing Assistant", layout="wide")

# Header and input field styles
st.markdown("""
    <h1 style='font-size: 2.5em;'>📚 <span style='color:#ffffff;'>StyleCraft:</span> Tailored Writing Assistant</h1>
    <p style='font-size: 1.1em;'>Welcome to StyleCraft, your personalized writing assistant. Configure your desired settings, and enter your topic below to generate tailored content.</p>

    <style>
        /* Custom bottom input box - positioned fully outside the sidebar */
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

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")

    learning_mode = st.checkbox("Learning Mode")

    selected_style = st.selectbox("Select a Writing Style:", list(style_descriptions.keys()))
    if learning_mode:
        st.markdown(f"**Description:** {style_descriptions[selected_style]}")

    selected_audience = st.selectbox("Select Your Target Audience:", list(audience_descriptions.keys()))
    if learning_mode:
        st.markdown(f"**Description:** {audience_descriptions[selected_audience]}")

    prompt_type = st.selectbox("Select Prompt Type:", list(prompt_type_descriptions.keys()))
    st.markdown(f"**Prompt Type Description:** {prompt_type_descriptions[prompt_type]}")

    if learning_mode:
        formality = st.slider("Formality Level", 1, 10, 5)
        complexity = st.slider("Complexity Level", 1, 10, 5)
        emotion = st.slider("Emotional Tone", 1, 10, 5)
    else:
        formality = 5
        complexity = 5
        emotion = 5

# Prompt generation logic
def construct_prompt(style, audience, topic, formality, complexity, emotion, prompt_type):
    style_text = style_descriptions[style]
    audience_text = audience_descriptions[audience]

    base = (
        f"You are a writer crafting content in the {style} style for {audience}.\n"
        f"Maintain tone and complexity levels — Formality: {formality}/10, Complexity: {complexity}/10, Emotional Tone: {emotion}/10.\n\n"
        f"Style Description: {style_text}\n"
        f"Audience Description: {audience_text}\n\n"
        f"Write about:\n{topic}"
    )

    if prompt_type == "Few-Shot":
        examples = (
            "\n\nExample 1: A professional email.\n"
            "Dear [Name],\nI’m writing to confirm my attendance at the interview scheduled for [Date]. I appreciate the opportunity.\n\n"
            "Example 2: A casual social post.\n"
            "Just dropped a new blog on productivity hacks — check it out! 💡 [link]\n\n"
        )
        return base + examples
    elif prompt_type == "Chain-of-Thought":
        return (
            "Let's reason step by step.\n"
            "First, analyze tone, audience, and content type...\n\n"
            + base
        )
    return base

# Input field (fixed and styled)
user_input = st.text_input("", placeholder="Enter your topic or prompt here...", key="user_input")

# Generate and display response
if user_input.strip():
    final_prompt = construct_prompt(
        selected_style, selected_audience, user_input,
        formality, complexity, emotion, prompt_type
    )
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(final_prompt)
    st.markdown(f"### ✍️ Generated Response ({prompt_type})")
    st.write(response.text)
