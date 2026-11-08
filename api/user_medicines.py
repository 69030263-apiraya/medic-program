import math

from flask import Blueprint, current_app, jsonify, request
from pymongo.errors import DuplicateKeyError, PyMongoError

from .database import get_user_medicines_collection
from .request_helpers import get_json_payload

user_medicines = Blueprint("user_medicines", __name__)


def valid_times_per_day(value) -> bool:
    return (
        isinstance(value, list)
        and all(
            isinstance(time, int) and not isinstance(time, bool) and time in (1, 2, 3, 4)
            for time in value
        )
        and len(value) == len(set(value))
    )


@user_medicines.get("/user/med")
def list_user_medicines():
    user_id = request.args.get("user_id")
    if not isinstance(user_id, str) or not user_id.strip():
        return jsonify({"error": "user_id_is_required"}), 400

    try:
        documents = get_user_medicines_collection().find(
            {"userId": user_id.strip()},
            {"_id": 0, "medId": 1, "timesPerDay": 1, "foodRequire": 1, "value": 1},
        )
        return jsonify(
            [
                {
                    "medId": document["medId"],
                    "timesPerDay": document["timesPerDay"],
                    "foodRequire": document["foodRequire"],
                    "value": document.get("value"),
                }
                for document in documents
            ]
        )
    except RuntimeError:
        current_app.logger.error("MONGODB_URI is not configured.")
        return jsonify({"error": "database_not_configured"}), 503
    except PyMongoError:
        current_app.logger.error("MongoDB request failed while listing user medicines.")
        return jsonify({"error": "database_unavailable"}), 503


@user_medicines.post("/user/med")
def add_user_medicine():
    payload, error_response = get_json_payload()
    if error_response:
        return error_response

    user_id = payload.get("userId")
    med_id = payload.get("medId")
    times_per_day = payload.get("timesPerDay")
    food_require = payload.get("foodRequire")
    value = payload.get("value")

    if not isinstance(user_id, str) or not user_id.strip():
        return jsonify({"error": "userId_is_required"}), 400
    if not isinstance(med_id, str) or not med_id.strip():
        return jsonify({"error": "medId_is_required"}), 400
    if not valid_times_per_day(times_per_day):
        return jsonify(
            {
                "error": "invalid_timesPerDay",
                "message": "timesPerDay must be an array of unique integers from 1 to 4.",
            }
        ), 400
    if "foodRequire" not in payload or food_require not in ("before", "after", None):
        return jsonify(
            {
                "error": "invalid_foodRequire",
                "message": "foodRequire must be 'before', 'after', or null.",
            }
        ), 400
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or value <= 0
        or (isinstance(value, float) and not math.isfinite(value))
    ):
        return jsonify(
            {
                "error": "invalid_value",
                "message": "value must be a positive number.",
            }
        ), 400

    user_id = user_id.strip()
    med_id = med_id.strip()
    try:
        user_meds = get_user_medicines_collection()
        user_meds.create_index(
            [("userId", 1), ("medId", 1)],
            unique=True,
        )
        if user_meds.find_one({"userId": user_id, "medId": med_id}, {"_id": 1}):
            return jsonify({"error": "user_medicine_already_exists"}), 409

        user_medicine = {
            "userId": user_id,
            "medId": med_id,
            "timesPerDay": times_per_day,
            "foodRequire": food_require,
            "value": value,
        }
        user_meds.insert_one(user_medicine)
        return jsonify(
            {
                "medId": med_id,
                "timesPerDay": times_per_day,
                "foodRequire": food_require,
                "value": value,
            }
        ), 201
    except DuplicateKeyError:
        return jsonify({"error": "user_medicine_already_exists"}), 409
    except RuntimeError:
        current_app.logger.error("MONGODB_URI is not configured.")
        return jsonify({"error": "database_not_configured"}), 503
    except PyMongoError:
        current_app.logger.error("MongoDB request failed while adding a user medicine.")
        return jsonify({"error": "database_unavailable"}), 503


@user_medicines.delete("/user/med")
def delete_user_medicine():
    payload, error_response = get_json_payload()
    if error_response:
        return error_response

    user_id = payload.get("userId")
    med_id = payload.get("medId")
    if not isinstance(user_id, str) or not user_id.strip():
        return jsonify({"error": "userId_is_required"}), 400
    if not isinstance(med_id, str) or not med_id.strip():
        return jsonify({"error": "medId_is_required"}), 400

    user_id = user_id.strip()
    med_id = med_id.strip()
    try:
        result = get_user_medicines_collection().delete_one(
            {"userId": user_id, "medId": med_id}
        )
        if result.deleted_count == 0:
            return jsonify({"error": "user_medicine_not_found"}), 404

        return jsonify(
            {"message": "successful", "userId": user_id, "medId": med_id}
        )
    except RuntimeError:
        current_app.logger.error("MONGODB_URI is not configured.")
        return jsonify({"error": "database_not_configured"}), 503
    except PyMongoError:
        current_app.logger.error("MongoDB request failed while deleting a user medicine.")
        return jsonify({"error": "database_unavailable"}), 503
