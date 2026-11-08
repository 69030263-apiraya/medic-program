from flask import jsonify, request
from werkzeug.exceptions import BadRequest


def get_json_payload():
    if not request.is_json:
        return None, (jsonify({"error": "content_type_must_be_application_json"}), 415)

    try:
        payload = request.get_json()
    except BadRequest:
        return None, (jsonify({"error": "invalid_request_body"}), 400)

    if not isinstance(payload, dict):
        return None, (jsonify({"error": "invalid_request_body"}), 400)

    return payload, None
