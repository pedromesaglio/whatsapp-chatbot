from openai import OpenAI
import shelve
from dotenv import load_dotenv
import os
import time
import logging
import requests  # Usaremos requests para interactuar con Ollama

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_MODEL_ID = os.getenv("OLLAMA_MODEL_ID")

if not OLLAMA_MODEL_ID:
    logging.error("OLLAMA_MODEL_ID is not set. Please check your .env file.")
    raise ValueError("OLLAMA_MODEL_ID is required but not set.")

client = OpenAI(api_key=OPENAI_API_KEY)


def upload_file(path):
    # Upload a file with an "assistants" purpose
    file = client.files.create(
        file=open("../../data/airbnb-faq.pdf", "rb"), purpose="assistants"
    )


def create_assistant(file):
    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name="WhatsApp AirBnb Assistant",
        instructions="You're a helpful WhatsApp assistant that can assist guests that are staying in our Paris AirBnb. Use your knowledge base to best respond to customer queries. If you don't know the answer, say simply that you cannot help with question and advice to contact the host directly. Be friendly and funny.",
        tools=[{"type": "retrieval"}],
        model="gpt-4-1106-preview",
        file_ids=[file.id],
    )
    return assistant


# Use context manager to ensure the shelf file is closed properly
def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)


def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id


def run_assistant(thread, name):
    """
    Enviar una solicitud a Ollama para generar una respuesta basada en el modelo especificado.
    """
    url = "http://localhost:11434/generate"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": OLLAMA_MODEL_ID,
        "prompt": f"Hola, {name}. {thread['content']}"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Lanza una excepción si la solicitud falla
        data = response.json()
        new_message = data.get("response", "No se pudo generar una respuesta.")
        logging.info(f"Generated message: {new_message}")
        return new_message
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al comunicarse con Ollama: {e}")
        raise


def generate_response(message_body, wa_id, name):
    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)

    # Si no existe un hilo, creamos uno
    if thread_id is None:
        logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = {"id": wa_id, "content": message_body}  # Simulamos un hilo
        store_thread(wa_id, thread["id"])
    else:
        logging.info(f"Retrieving existing thread for {name} with wa_id {wa_id}")
        thread = {"id": thread_id, "content": message_body}  # Simulamos un hilo existente

    # Ejecutar el asistente y obtener el nuevo mensaje
    new_message = run_assistant(thread, name)

    return new_message