from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from clients import load_clients, find_client

app = Flask(__name__)
CORS(app)

openai.api_key = "YOUR_OPENAI_API_KEY"

SYSTEM_PROMPT = """Sei responsabile nella raccolta di ordini ittici da ristoranti. 
Il tuo compito è dialogare in modo educato ma gioviale, aiutando i ristoratori a completare il loro ordine in modo preciso se ci sono ambiguità o dati mancanti.

I dati obbligatori sono:
1. Nome del ristorante
2. Elenco dei prodotti ordinati, ciascuno con una quantità numerica
3. Indicazioni sul quando consegnare

Non proporre prodotti.
Non completare l'ordine se manca uno di questi tre dati.
Riepiloga con chiarezza solo quando hai tutti i dati necessari.
Se riconosci il ristorante, puoi arricchire la risposta con le informazioni note (es. preferenze o indirizzo)."""

clients_data = load_clients()
conversation_history = []

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    conversation_history.append({"role": "user", "content": user_message})

    client_info = find_client(user_message, clients_data)

    if client_info:
        conversation_history.append({"role": "system", "content": f"Cliente riconosciuto: {client_info}"})
    else:
        conversation_history.append({"role": "system", "content": "⚠️ Il cliente non è registrato. Verrà contattato dalla direzione per conferma."})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=1.0
    )

    reply = response.choices[0].message.content.strip()
    conversation_history.append({"role": "assistant", "content": reply})

    return jsonify({"reply": reply})