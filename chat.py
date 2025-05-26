import os
import json
import openai
from flask import Blueprint, request, jsonify

chat_bp = Blueprint('chat', __name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Prompt da file + istruzioni su formato JSON
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

INSTRUCTIONS = (
    "\nRispondi SOLO con un JSON nel formato:\n"
    "{\n"
    "  \"customer_name\": string or null,\n"
    "  \"order_items\": [ { \"product\": string, \"quantity\": number } ] or null,\n"
    "  \"delivery_time\": string or null,\n"
    "  \"message\": risposta naturale e cordiale al cliente (ma non inventare o proporre)\n"
    "}\n"
    "Non aggiungere spiegazioni, saluti, testo prima o dopo il JSON."
)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "")
        history = data.get("history", [])

        messages = [{"role": "system", "content": SYSTEM_PROMPT + INSTRUCTIONS}] + history + [
            {"role": "user", "content": message}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        raw_reply = response.choices[0].message["content"]

        # Tentativo parsing JSON
        try:
            start = raw_reply.find("{")
            end = raw_reply.rfind("}") + 1
            json_part = raw_reply[start:end]
            parsed_json = json.loads(json_part)
        except Exception as ex:
            return jsonify({
                "error": "Risposta non strutturata correttamente",
                "raw": raw_reply
            }), 500

        customer_ok = parsed_json.get("customer_name") not in [None, "", "null"]
        date_ok = parsed_json.get("delivery_time") not in [None, "", "null"]

        order_complete = customer_ok and date_ok

        return jsonify({
            "response_text": parsed_json.get("message", "[nessuna risposta]"),
            "order_complete": order_complete,
            "customer_name": parsed_json.get("customer_name"),
            "delivery_time": parsed_json.get("delivery_time"),
            "order_items": parsed_json.get("order_items", []),
            "history": messages + [{"role": "assistant", "content": raw_reply}]
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "trace": repr(e)
        }), 500
