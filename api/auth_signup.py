import re
import uuid

from flask import Blueprint, current_app, jsonify
from pymongo.errors import DuplicateKeyError, PyMongoError
from werkzeug.security import generate_password_hash

from .audit import audited_response
from .database import get_users_collection
from .request_helpers import get_json_payload

auth_signup = Blueprint("auth_signup", __name__)


@auth_signup.post("/auth/signup")
def signup():
    payload, error_response = get_json_payload()
    if error_response:
        response, status_code = error_response
        return audited_response(None, "auth.signup", "invalid_request", response, status_code)

    user_name = payload.get("userName")
    password = payload.get("userPassword")
    if not isinstance(user_name, str) or not re.fullmatch(r"[A-Za-z0-9_]{3,30}", user_name):
        return audited_response(
            None,
            "auth.signup",
            "invalid_userName",
            jsonify(
                {
                    "error": "invalid_userName",
                    "message": "userName must be 3-30 characters using letters, numbers, and underscores.",
                }
            ),
            400,
        )
    if not isinstance(password, str) or len(password) < 4:
        return audited_response(
            None,
            "auth.signup",
            "invalid_userPassword",
            jsonify(
                {
                    "error": "invalid_userPassword",
                    "message": "userPassword must be at least 4 characters.",
                }
            ),
            400,
        )

    try:
        users = get_users_collection()
        users.create_index("userName", unique=True)
        existing_user = users.find_one(
            {"userName": user_name}, {"_id": 1, "userId": 1}
        )
        if existing_user is not None:
            existing_user_id = str(existing_user.get("userId") or existing_user.get("_id"))
            return audited_response(
                existing_user_id,
                "auth.signup",
                "username_already_exists",
                jsonify({"error": "username_already_exists"}),
                409,
            )

        user_id = str(uuid.uuid4())
        users.insert_one(
            {
                "userId": user_id,
                "userName": user_name,
                "userPassword": generate_password_hash(password),
                "userRole": "user",
            }
        )
        return audited_response(
            user_id,
            "auth.signup",
            "success",
            jsonify(
                {
                    "message": "successful",
                    "userId": user_id,
                    "userName": user_name,
                    "userRole": "user",
                }
            ),
            200,
        )
    except DuplicateKeyError:
        return audited_response(
            None,
            "auth.signup",
            "username_already_exists",
            jsonify({"error": "username_already_exists"}),
            409,
        )
    except RuntimeError:
        current_app.logger.error("MONGODB_URI is not configured.")
        return audited_response(
            None,
            "auth.signup",
            "database_not_configured",
            jsonify({"error": "database_not_configured"}),
            503,
        )
    except PyMongoError:
        current_app.logger.error("MongoDB request failed during signup.")
        return audited_response(
            None,
            "auth.signup",
            "database_unavailable",
            jsonify({"error": "database_unavailable"}),
            503,
        )
