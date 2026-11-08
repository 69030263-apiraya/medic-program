from flask import Blueprint, jsonify

from .audit import audited_response
from .request_helpers import get_json_payload

auth_logout = Blueprint("auth_logout", __name__)


@auth_logout.post("/auth/logout")
def logout():
    payload, error_response = get_json_payload()
    if error_response:
        response, status_code = error_response
        return audited_response(None, "auth.logout", "invalid_request", response, status_code)

    user_id = payload.get("userId")
    if not isinstance(user_id, str) or not user_id.strip():
        return audited_response(
            None,
            "auth.logout",
            "userId_is_required",
            jsonify({"error": "userId_is_required"}),
            400,
        )

    return audited_response(
        user_id,
        "auth.logout",
        "success",
        jsonify({"message": "successful", "userId": user_id}),
        200,
    )
