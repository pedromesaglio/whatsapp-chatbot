import logging
import json

from flask import Blueprint, request, jsonify, current_app

from .decorators.security import signature_required
from .utils.whatsapp_utils import (
    process_whatsapp_message,
    is_valid_whatsapp_message,
)

webhook_blueprint = Blueprint("webhook", __name__)

def handle_message():
    """
    Handle incoming webhook events from the WhatsApp API.

    This function processes incoming WhatsApp messages and other events,
    such as delivery statuses. If the event is a valid message, it gets
    processed. If the incoming payload is not a recognized WhatsApp event,
    an error is returned.

    Every message send will trigger 4 HTTP requests to your webhook: message, sent, delivered, read.

    Returns:
        response: A tuple containing a JSON response and an HTTP status code.
    """
    body = request.get_json()
    logging.info(f"Received request body: {body}")

    # Check if it's a WhatsApp status update
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        logging.info("Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200

    try:
        if is_valid_whatsapp_message(body):
            logging.info("Valid WhatsApp message received. Processing...")
            process_whatsapp_message(body)
            return jsonify({"status": "ok"}), 200
        else:
            logging.warning("Received an invalid WhatsApp API event.")
            return (
                jsonify({"status": "error", "message": "Not a WhatsApp API event"}),
                404,
            )
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON")
        return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


# Required webhook verification for WhatsApp
def verify():
    """
    Verifies the webhook with the token provided by WhatsApp.
    """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == current_app.config["VERIFY_TOKEN"]:
            logging.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            logging.warning("Verification failed: Invalid token.")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        logging.warning("Verification failed: Missing parameters.")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400


@webhook_blueprint.route("/webhook", methods=["GET"])
def webhook_get():
    """
    Handles the GET request for webhook verification.
    """
    return verify()


@webhook_blueprint.route("/webhook", methods=["POST"])
@signature_required
def webhook_post():
    """
    Handles the POST request for incoming webhook events.
    """
    return handle_message()

# Register the blueprint in the application
def register_blueprints(app):
    """
    Registers all blueprints in the Flask application.
    """
    app.register_blueprint(webhook_blueprint, url_prefix="/webhook")
    logging.info("Webhook blueprint registered successfully.")
