import logging
import sys
from flask import request, jsonify  # Importamos request y jsonify para manejar solicitudes y respuestas
import requests  # Usaremos requests para interactuar con Ollama
from ollama_client import OllamaClient  # Importamos el cliente de Ollama

# Add the root directory to sys.path
sys.path.append("/home/pedro/Desktop/whatsapp-bot/python-whatsapp-bot")

from app import create_app


app = create_app()
ollama_client = OllamaClient()  # Inicializamos el cliente

@app.route("/ollama", methods=["POST"])
def ollama_interact():
    """
    Endpoint para interactuar con Ollama.
    """
    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    response = ollama_client.send_message(data["message"])
    if "error" in response:
        return jsonify(response), 500

    return jsonify(response)

if __name__ == "__main__":
    logging.info("Flask app started")
    app.run(host="0.0.0.0", port=8000)
