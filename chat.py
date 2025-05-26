import os
import json
import openai
from flask import Blueprint, request, jsonify

chat_bp = Blueprint('chat', __name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = (
    "Agisci come un assistente che riceve ordini di pesce da ristoratori campani. "
    "Fai domande per ottenere: nome del cliente, cosa vuole ordinare (quantità e prodotto), "
    "e quando desidera riceverlo. Non confermare l'ordine finché mancano dati. "
    "Rispondi in modo amichevole ma professionale, come un esperto di pescheria."
)

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

        order_complete = any(x in reply.lower() for x in ["grazie per l'ordine", "ricevuto", "conferma", "è tutto", "consegna"])

        return jsonify({
            "response_text": reply,
            "order_complete": order_complete,
            "history": messages + [{"role": "assistant", "content": reply}]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
