
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
3. Quando consegnare

Non proporre prodotti.
Non completare l'ordine se manca uno di questi tre dati.
Riepiloga con chiarezza solo quando hai tutti i dati necessari."""

FEW_SHOTS = [
    {"role": "user", "content": "Per domani cala 15 kg tonno rosso sv atm 100 fasolari 100 tozze 3 kg fasolari 3 kg tozze"},
    {"role": "assistant", "content": "ciao, grazie. Per domani, ristorante Cala Moresca, 15 Kg di Tonno Rosso sottovuoto, 100 Vongole Tozze, 3 Kg di Fasolari e 3 Kg di Cozze. Va bene così? Grazie molte "},
    {"role": "user", "content": "Rosolino per domani 1 kg di alici senza testa Calamaretti 2 kg Spigoloni 5 pz Grazie"},
    {"role": "assistant", "content": "Certo ristorante Rosolino. 1 Kg di Alici senza testa, Calamaretti per 2 Kg, 5 Spigoloni. Bene così?  "},
    {"role": "user", "content": "si basta così"},
    {"role": "assistant", "content": "ok ciao"},
    {"role": "user", "content": "Corallum 1 kg alici 3 kg tonno"},
    {"role": "assistant", "content": "Ristorante Corallum, 1 Kg di Alici e 3 Kg di Tonno. Per quando?"},
    {"role": "user", "content": "Lunedì 26 giugno alle 11"},
    {"role": "assistant", "content": "Perfetto, consegna lunedì 26 giugno alle 11 per il ristorante Corallum: 1 Kg di Alici, 3 Kg di Tonno."}
]

conversation_history = []

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    conversation_history.append({"role": "user", "content": user_message})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + FEW_SHOTS + conversation_history

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.8
        )
        reply = response.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": reply})
    except Exception as e:
        reply = f"Errore nella risposta del modello: {str(e)}"

    return jsonify({"reply": reply})
