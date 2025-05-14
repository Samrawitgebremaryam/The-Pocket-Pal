# 🌍 The Traveler’s Pocket Pal 

**Smart Travel Companion Powered by Multi-Agent Collaboration**

## 📖 Overview

This document provides a comprehensive specification and setup plan for **The Traveler’s Pocket Pal **, a lightweight, AI-powered web application designed to assist travelers abroad.

The project demonstrates the **A2A (Agent-to-Agent)** protocol for multi-agent communication and the **MCP (Model Context Protocol)** for external tool integration, using a Streamlit front end. It includes three agents with distinct roles, leveraging two external APIs as MCP tools, and a clear folder structure to ensure modularity and ease of development.

---

## 🧠 Project Concept and Purpose

**The Traveler’s Pocket Pal** is a user-friendly web application that supports travelers outside their home country by providing a tailored "Pocket Guide" with two core functionalities:

- **Spot Recommendations**: Suggests places to eat, visit, or shop based on the user’s destination and specific need.
    - _Example_: “Finding quick meals” in “Barcelona, Spain” → “La Boqueria Market, a vibrant spot for quick tapas.”
- **Phrase Translation**: Translates a user-provided phrase into the local language for effective communication.
    - _Example_: “Can I have this to go?” in Spanish → “¿Puedo llevar esto para llevar?”

---
## 📸 Init

![Init Image](https://media.licdn.com/dms/image/v2/D5622AQGtBESqSfcjsQ/feedshare-shrink_1280/B56ZY5c2cXH0Ak-/0/1744720592440?e=2147483647&v=beta&t=9JCK9BHTB0oTDTxXxCinQMdZocjALKkSNt9yYgnXBAg)  
*This image visually represents A2A and MCP protocols that form the core of The Traveler’s Pocket Pal.*
---
## 🎯 Purpose

- **Demonstrate A2A Protocol**: Showcases how three agents collaborate, with Agent 1 (Orchestrator) delegating tasks to Agent 2 (Spot Finder) and Agent 3 (Phrase Translator).
- **Highlight MCP Integration**: Integrates OpenStreetMap (for location) and Google Translate (for language) as MCP tools.
- **Provide Practical Utility**: Offers actionable advice and translations for daily travel tasks.

---

## ✨ Why It’s Unique

- **Practical and Focused**: Addresses real-world travel needs with a simple UI.
- **Technical Showcase**: Highlights agent modularity and API integration.
- **Educational Value**: Serves as a reference for distributed AI system design.

---

## 👥 Target Audience

- **Travelers Abroad**
- **Language Beginners**
- **Technical Demonstrators** (students, educators, developers)

---

## ⚙️ Functionality Overview

### 👤 User Input
- Destination (e.g., "Barcelona, Spain")
- Need (e.g., "Finding quick meals")
- Phrase (e.g., "Can I have this to go?")

### 🔁 Task Orchestration
- Agent 1 processes input and uses A2A to delegate tasks to Agents 2 and 3.

### 🧠 Task Execution
- Agent 2 → Uses OpenStreetMap (MCP) for spot recommendations.
- Agent 3 → Uses Google Translate (MCP) for translation.

### 📤 Output Delivery
- Agent 1 compiles results and sends them to Streamlit UI.

---

## 🧪 Example Scenarios

### Scenario 1: Finding Quick Meals + Translation
**Input**: “Barcelona, Spain”; “Finding quick meals”; “Can I have this to go?”  
**Output**:
- Recommended Spots:
    - La Boqueria Market
    - El Quim de la Boqueria
- Translated Phrase: _¿Puedo llevar esto para llevar?_

### Scenario 2: Finding Affordable Shops + Translation
**Input**: “Tokyo, Japan”; “Finding affordable shops”; “How much is this?”  
**Output**:
- Recommended Spots:
    - Daiso in Shibuya
    - Don Quijote
- Translated Phrase: _これはいくらですか？ (Kore wa ikura desu ka?)_

---

## 🗂️ Project Structure

```bash
pocket-pal/
│
├── agents/                  # Flask-based sub-agents
│   ├── spot_agent/          # Agent 2: Spot Finder
│   └── translation_agent/   # Agent 3: Phrase Translator
│
├── main_agent/              # Agent 1: Orchestrator
├── interface/               # Streamlit-based UI
├── utils/                   # Common utilities
├── assets/                  # Static files (images, icons)
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## 🚀 How to Run

```bash
# Step 1: Clone Repo
git clone https://github.com/your-username/pocket-pal.git
cd pocket-pal

# Step 2: Set up virtual environment
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
pip install -r requirements.txt

# Step 3: Run agents
cd agents/spot_agent && flask run --port=5001
cd ../translation_agent && flask run --port=5002

# Step 4: Run main orchestrator
cd ../../main_agent && flask run --port=5000

# Step 5: Run Streamlit UI
cd ../interface && streamlit run app.py
```

---

## 💬 Protocols

### A2A (Agent-to-Agent Protocol)
Agents communicate indirectly through the orchestrator agent. Each agent performs isolated tasks independently and returns results.

### MCP (Model Context Protocol)
External APIs (e.g., Google Translate, OpenStreetMap) are invoked by agents as tools for completing their assigned tasks.

---

## 💡 Technologies Used

- **Python 3.10+**
- **Flask**
- **Streamlit**
- **REST APIs** (OpenStreetMap, Google Translate)
- **NLP**

---
