import json
import re

CLIENTS_FILE = "clients.json"

def load_clients():
    try:
        with open(CLIENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def find_client(message, clients):
    message_lower = message.lower()
    for key, data in clients.items():
        if key in message_lower:
            return f"{data['nome']} ({data.get('referente', '')})"
    return None