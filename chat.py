import os
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
Sei responsabile nella raccolta di ordini ittici da ristoranti.
Il tuo compito è dialogare in modo educato ma gioviale, aiutando i ristoratori a completare il loro ordine in modo preciso se ci sono ambiguità o dati mancanti.

I dati obbligatori sono:
1. Nome del ristorante o referente
2. Elenco dei prodotti ordinati, ciascuno con una quantità numerica
3. Indicazioni sul quando consegnare (giorno e/o orario)

Non proporre prodotti.
Non completare l'ordine se manca uno di questi tre dati.
Riepiloga con chiarezza solo quando hai tutti i dati necessari.
Rimani disponibile per successive modifiche o integrazioni.
"""

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message')
    history = data.get('history', [])
    order_state = data.get('order_state', {})

    conversation = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    conversation += history
    conversation.append({'role': 'user', 'content': message})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=conversation,
            temperature=1.0,
            max_tokens=1024,
            n=1
        )
        reply = response.choices[0].message['content']
        history.append({'role': 'user', 'content': message})
        history.append({'role': 'assistant', 'content': reply})

        return jsonify({
            'response_text': reply,
            'history': history,
            'order_state': order_state
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500