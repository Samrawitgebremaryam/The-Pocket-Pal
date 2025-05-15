#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "Starting Agent 2 (Spot Finder)..."
python spot_finder/main.py > spot_finder.log 2>&1 &
sleep 2
echo "Starting Agent 3 (Phrase Translator)..."
python phrase_translator/main.py > phrase_translator.log 2>&1 &
sleep 2
echo "Starting Agent 1 (Streamlit)..."
python -m streamlit run streamlit_app.py