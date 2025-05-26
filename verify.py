import json
from flask import Blueprint, request, jsonify

verify_bp = Blueprint('verify', __name__)

@verify_bp.route("/verify", methods=["POST"])
def verify():
    try:
        data = request.get_json()

        customer = data.get("customer_name", "").lower()
        order = data.get("order_content", "").lower()

        if "donato" not in customer:
            return jsonify({"success": False, "message": "Cliente non trovato."})
        if "gamberi" not in order:
            return jsonify({"success": False, "message": "Prodotto richiesto non disponibile."})

        return jsonify({"success": True, "message": "Ordine confermato. Grazie!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
