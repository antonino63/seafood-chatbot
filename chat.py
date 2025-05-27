import os
import json
from flask import Blueprint, request, jsonify
import openai

chat_bp = Blueprint("chat", __name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Lettura system prompt
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# Istruzioni forti
INSTRUCTIONS = (
    "\n\n🔒 Rispondi SOLO con un JSON nel formato esatto seguente. "
    "NON aggiungere saluti, spiegazioni o testo prima o dopo. "
    "Usa solo i campi richiesti, anche se incompleti. Se un dato non è presente, metti null.\n"
    "{\n"
    "  \"customer_name\": string or null,\n"
    "  \"order_items\": [ { \"product\": string, \"quantity\": number } ] or null,\n"
    "  \"delivery_time\": string or null,\n"
    "  \"message\": string\n"
    "}\n"
)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "")
        history = data.get("history", [])

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + INSTRUCTIONS}
        ] + history + [
            {"role": "user", "content": message}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        raw_reply = response.choices[0].message["content"]

        # Fallback JSON extraction
        try:
            start = raw_reply.find("{")
            end = raw_reply.rfind("}") + 1
            json_part = raw_reply[start:end]
            parsed = json.loads(json_part)
        except Exception:
            return jsonify({
                "error": "Risposta non strutturata correttamente",
                "raw": raw_reply
            }), 500

        order_complete = all([
            parsed.get("customer_name"),
            parsed.get("delivery_time")
        ])

        return jsonify({
            "response_text": parsed.get("message", "[nessuna risposta]"),
            "order_complete": order_complete,
            "customer_name": parsed.get("customer_name"),
            "delivery_time": parsed.get("delivery_time"),
            "order_items": parsed.get("order_items", []),
            "history": messages + [{"role": "assistant", "content": raw_reply}]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Endpoint di debug prompt
@chat_bp.route("/debug-prompt", methods=["GET"])
def debug_prompt():
    return jsonify({
        "system_prompt": SYSTEM_PROMPT[:500] + "..."
    })
