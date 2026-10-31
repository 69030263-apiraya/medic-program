import time

from flask import Response, current_app, jsonify
from pymongo.errors import PyMongoError

from .database import get_user_logs_collection


def write_user_log(user_id: str | None, action: str, result: str) -> None:
    get_user_logs_collection().insert_one(
        {
            "userId": user_id,
            "action": action,
            "result": result,
            "timestamp": int(time.time()),
        }
    )


def audited_response(
    user_id: str | None,
    action: str,
    result: str,
    response: Response,
    status_code: int,
) -> tuple[Response, int]:
    try:
        write_user_log(user_id, action, result)
    except RuntimeError:
        current_app.logger.error("MONGODB_URI is not configured; auth action could not be logged.")
        return jsonify({"error": "database_not_configured"}), 503
    except PyMongoError:
        current_app.logger.error("MongoDB request failed while writing an auth audit log.")
        return jsonify({"error": "audit_log_unavailable"}), 503

    return response, status_code
