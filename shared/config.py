# Configuration for agent endpoints and API settings
AGENT2_URL = "http://localhost:5002/spot_finder"
AGENT3_URL = "http://localhost:5003/phrase_translator"
NOMINATIM_USER_AGENT = "TravelersPocketPal/1.0 (samrawitgebremaryam121@gmail.com)"


# Configuration for agent endpoints and API settings
AGENT_CARDS = {
    "agent_1": {
        "id": "agent_1",
        "role": "orchestrator",
        "tasks": ["random", "translate", "spot_finder"],
        "endpoint": None,
        "mcp_schema": {"task": str, "data": dict}
    },
    "agent_2": {
        "id": "agent_2",
        "role": "spot_finder",
        "tasks": ["spot_finder"],
        "endpoint": "http://localhost:5002/spot_finder",
        "mcp_schema": {"destination": str, "need": str}
    },
    "agent_3": {
        "id": "agent_3",
        "role": "phrase_translator",
        "tasks": ["translate"],
        "endpoint": "http://localhost:5003/phrase_translator",
        "mcp_schema": {"phrase": str, "source_lang": str, "target_lang": str}
    }
}

