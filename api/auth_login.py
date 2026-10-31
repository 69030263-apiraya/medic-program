from flask import Blueprint, current_app, jsonify
from pymongo.errors import PyMongoError
from werkzeug.security import generate_password_hash

from .audit import audited_response
from .database import get_users_collection
from .passwords import verify_password
from .request_helpers import get_json_payload

auth_login = Blueprint("auth_login", __name__)


@auth_login.post("/auth/login")
def login():
    payload, error_response = get_json_payload()
    if error_response:
        response, status_code = error_response
        return audited_response(None, "auth.login", "invalid_request", response, status_code)

    user_name = payload.get("userName")
    password = payload.get("userPassword")
    if not isinstance(user_name, str) or not user_name.strip():
        return audited_response(
            None, "auth.login", "userName_is_required",
            jsonify({"error": "userName_is_required"}), 400
        )
    if not isinstance(password, str) or not password:
        return audited_response(
            None, "auth.login", "userPassword_is_required",
            jsonify({"error": "userPassword_is_required"}), 400
        )

    try:
        users = get_users_collection()
        user = users.find_one({"userName": user_name.strip()})
        user_id = (
            str(user.get("userId") or user["_id"])
            if user is not None and ("userId" in user or "_id" in user)
            else None
        )
        if (
            user is None
            or not isinstance(user.get("userPassword"), str)
            or not verify_password(user["userPassword"], password)
        ):
            return audited_response(
                user_id,
                "auth.login",
                "invalid_credentials",
                jsonify({"error": "invalid_credentials"}),
                401,
            )
        if (
            not isinstance(user.get("userName"), str)
            or not isinstance(user.get("userRole"), str)
            or "_id" not in user
        ):
            current_app.logger.error("A user record is missing required identity fields.")
            return audited_response(
                user_id,
                "auth.login",
                "invalid_user_record",
                jsonify({"error": "invalid_user_record"}),
                500,
            )

        if not user["userPassword"].startswith(("scrypt:", "pbkdf2:")):
            result = users.update_one(
                {"_id": user["_id"], "userPassword": user["userPassword"]},
                {"$set": {"userPassword": generate_password_hash(password)}},
            )
            if result.matched_count == 0:
                user = users.find_one({"_id": user["_id"]})
                if (
                    user is None
                    or not isinstance(user.get("userPassword"), str)
                    or not verify_password(user["userPassword"], password)
                ):
                    return audited_response(
                        user_id,
                        "auth.login",
                        "invalid_credentials",
                        jsonify({"error": "invalid_credentials"}),
                        401,
                    )
                if (
                    not isinstance(user.get("userName"), str)
                    or not isinstance(user.get("userRole"), str)
                    or "_id" not in user
                ):
                    current_app.logger.error("A user record is missing required identity fields.")
                    return audited_response(
                        user_id,
                        "auth.login",
                        "invalid_user_record",
                        jsonify({"error": "invalid_user_record"}),
                        500,
                    )

        return audited_response(
            user_id,
            "auth.login",
            "success",
            jsonify(
                {
                    "userId": str(user.get("userId") or user["_id"]),
                    "userName": user["userName"],
                    "userRole": user["userRole"],
                }
            ),
            200,
        )
    except RuntimeError:
        current_app.logger.error("MONGODB_URI is not configured.")
        return audited_response(
            None,
            "auth.login",
            "database_not_configured",
            jsonify({"error": "database_not_configured"}),
            503,
        )
    except PyMongoError:
        current_app.logger.error("MongoDB request failed during login.")
        return audited_response(
            None,
            "auth.login",
            "database_unavailable",
            jsonify({"error": "database_unavailable"}),
            503,
        )
