from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """Sei responsabile nella raccolta di ordini ittici da ristoranti. 
Il tuo compito è dialogare in modo educato ma gioviale, aiutando i ristoratori a completare il loro ordine in modo preciso se ci sono ambiguità o dati mancanti.

I dati obbligatori sono:
1. Nome del ristorante
2. Elenco dei prodotti ordinati, ciascuno con una quantità numerica
3. Indicazioni sul quando consegnare

Non proporre prodotti.
Non completare l'ordine se manca uno di questi tre dati.
Riepiloga con chiarezza solo quando hai tutti i dati necessari."""

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=1.0
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"Errore nella risposta del modello: {str(e)}"

    return jsonify({"reply": reply})
