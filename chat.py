import os
import json
import openai
from flask import Blueprint, request, jsonify

chat_bp = Blueprint('chat', __name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Caricamento del system prompt dal file
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "")
        history = data.get("history", [])

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [
            {"role": "user", "content": message}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        reply = response.choices[0].message["content"]

        # Verifica rudimentale: presenza dei campi essenziali
        conversation_text = " ".join([m["content"] for m in messages if m["role"] != "system"]).lower()

        has_customer = any(x in conversation_text for x in ["ristorante", "cliente", "osteria", "trattoria", "bersagliera", "donato"])
        has_date = any(x in conversation_text for x in ["oggi", "domani", "dopodomani", "alle", "ore", "stasera", "questa sera", "mattina", "pomeriggio"])

        order_complete = has_customer and has_date

        return jsonify({
            "response_text": reply,
            "order_complete": order_complete,
            "history": messages + [{"role": "assistant", "content": reply}]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
