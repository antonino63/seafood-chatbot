import os
import json
from flask import Blueprint, request, jsonify
import openai

chat_bp = Blueprint("chat", __name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

INSTRUCTIONS = (
    """
✨ Sei un assistente chatbot per ristoratori che ordinano prodotti ittici.
Obiettivo:
1. Estrai il nome del cliente (ristorante o referente)
2. Estrai l'elenco dei prodotti ordinati con quantità (solo numeri)
3. Estrai giorno e orario desiderato per la consegna

Comportamento:
- Non proporre prodotti. Non confermare se mancano dati obbligatori.
- Rispondi sempre con un tono cortese e chiaro.
- Quando tutti i dati sono presenti, riepiloga e saluta.

Esempi:
{
  "customer_name": "Donato",
  "order_items": [
    {"product": "spigole", "quantity": 2}
  ],
  "delivery_time": "domani alle 10",
  "message": "Perfetto, ho segnato 2 kg di spigole per domani alle 10 a nome di Donato. Grazie!"
}
{
  "customer_name": "Bersagliera",
  "order_items": [
    {"product": "triglie genovesi", "quantity": 100},
    {"product": "astici congelati", "quantity": 2},
    {"product": "cozze di Napoli", "quantity": 1}
  ],
  "delivery_time": "sabato prima di pranzo",
  "message": "Perfetto, ho segnato l'ordine per Bersagliera per sabato prima di pranzo. Grazie!"
}
{
  "customer_name": "Caracol",
  "order_items": [
    {"product": "lupini", "quantity": 5}
  ],
  "delivery_time": "domani",
  "message": "Ho preso nota di 5 kg di lupini per domani a nome Caracol."
}
{
  "customer_name": "Rosolino",
  "order_items": [
    {"product": "alici senza testa", "quantity": 1},
    {"product": "calamaretti", "quantity": 2},
    {"product": "spigoloni", "quantity": 5}
  ],
  "delivery_time": "domani",
  "message": "Ordine ricevuto per Rosolino."
}
{
  "customer_name": "Fenestella",
  "order_items": [
    {"product": "misto", "quantity": 5},
    {"product": "vongole", "quantity": 5},
    {"product": "astici", "quantity": 5},
    {"product": "taratufi", "quantity": 3},
    {"product": "tonno", "quantity": 1},
    {"product": "cozze", "quantity": 20}
  ],
  "delivery_time": "domani",
  "message": "Grazie Davide. L'ordine è confermato per domani."
}

⚠️ Rispondi solo con un JSON strutturato come sopra, senza testo esterno.
"""
)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "")
        history = data.get("history", [])
        order_state = data.get("order_state", {
            "customer_name": None,
            "delivery_time": None,
            "order_items": []
        })

        order_context = f"\n\nOrdine finora:\nCliente: {order_state['customer_name']}\nConsegna: {order_state['delivery_time']}\nProdotti: {order_state['order_items']}"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + INSTRUCTIONS + order_context}
        ] + history + [
            {"role": "user", "content": message}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.6
        )

        raw_reply = response.choices[0].message["content"]

        try:
            start = raw_reply.find("{")
            end = raw_reply.rfind("}") + 1
            json_part = raw_reply[start:end]
            parsed = json.loads(json_part)
        except Exception:
            return jsonify({
                "response_text": raw_reply.strip() or "[nessuna risposta]",
                "raw": raw_reply,
                "error": "Risposta non JSON, fallback attivato"
            }), 200

        if parsed.get("customer_name"):
            order_state["customer_name"] = parsed["customer_name"]
        if parsed.get("delivery_time"):
            order_state["delivery_time"] = parsed["delivery_time"]
        if parsed.get("order_items"):
            order_state["order_items"] += parsed["order_items"]

        order_complete = all([
            order_state.get("customer_name"),
            order_state.get("delivery_time"),
            order_state.get("order_items")
        ])

        return jsonify({
            "response_text": parsed.get("message", "[nessuna risposta]"),
            "order_complete": order_complete,
            "customer_name": order_state.get("customer_name"),
            "delivery_time": order_state.get("delivery_time"),
            "order_items": order_state.get("order_items", []),
            "order_state": order_state,
            "history": messages + [{"role": "assistant", "content": raw_reply}]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route("/debug-prompt", methods=["GET"])
def debug_prompt():
    return jsonify({"system_prompt": SYSTEM_PROMPT[:500] + "..."})
