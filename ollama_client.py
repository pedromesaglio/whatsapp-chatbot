import requests
import logging

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434/api/chat"):
        self.base_url = base_url

    def send_message(self, message):
        """
        Envía un mensaje a Ollama y devuelve la respuesta.
        """
        payload = {"message": message}
        try:
            response = requests.post(self.base_url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al interactuar con Ollama: {e}")
            return {"error": "Failed to communicate with Ollama"}
