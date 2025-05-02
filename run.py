import logging
import sys
from flask import request, jsonify  # Importamos request y jsonify para manejar solicitudes y respuestas
import requests  # Usaremos requests para interactuar con Ollama
from ollama_client import OllamaClient  # Importamos el cliente de Ollama

# Add the root directory to sys.path
sys.path.append("/home/pedro/Desktop/whatsapp-bot/python-whatsapp-bot")

from app import create_app
from app.services.openai_service import process_prompts  # Importamos la nueva función

app = create_app()
ollama_client = OllamaClient()  # Inicializamos el cliente

@app.route("/ollama", methods=["POST"])
def ollama_interact():
    """
    Endpoint para interactuar con Ollama.
    """
    data = request.json
    logging.info(f"Received request data: {data}")

    if not data or "message" not in data:
        logging.error("Invalid request: 'message' field is missing.")
        return jsonify({"error": "No message provided"}), 400

    try:
        response = ollama_client.send_message(data["message"])
        logging.info(f"Ollama response: {response}")

        if "error" in response:
            logging.error(f"Ollama returned an error: {response['error']}")
            return jsonify(response), 500

        return jsonify(response)

    except Exception as e:
        logging.error(f"Unexpected error while communicating with Ollama: {e}")
        return jsonify({"error": "Failed to communicate with Ollama"}), 500

@app.route("/", methods=["GET"])
def root_redirect():
    """
    Redirige las solicitudes de la raíz al endpoint /webhook.
    """
    return jsonify({"error": "Invalid endpoint. Use /webhook instead."}), 404

if __name__ == "__main__":
    logging.info("Flask app started")
    process_prompts()  # Ejecutamos el procesamiento de prompts
    app.run(host="0.0.0.0", port=8000)
