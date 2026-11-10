import math
from datetime import date, datetime, timezone

from flask import Blueprint, current_app, jsonify, request
from pymongo.errors import DuplicateKeyError, PyMongoError

from .database import (
    get_medicines_collection,
    get_user_medic_logs_collection,
    get_user_medicines_collection,
)
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


@user_medicines.post("/user/med/log")
def record_medication_status():
    payload, error_response = get_json_payload()
    if error_response:
        return error_response

    user_id = payload.get("userId")
    med_ids = payload.get("medIds")
    period_id = payload.get("periodId")
    status = payload.get("status")
    scheduled_date = payload.get("date")

    if not isinstance(user_id, str) or not user_id.strip():
        return jsonify({"error": "userId_is_required"}), 400
    if not isinstance(med_ids, list) or not med_ids or any(
        not isinstance(med_id, str) or not med_id.strip() for med_id in med_ids
    ):
        return jsonify({"error": "invalid_medIds"}), 400
    med_ids = [med_id.strip() for med_id in med_ids]
    if len(med_ids) != len(set(med_ids)):
        return jsonify({"error": "invalid_medIds"}), 400
    if (
        not isinstance(period_id, int)
        or isinstance(period_id, bool)
        or period_id not in (1, 2, 3, 4)
    ):
        return jsonify({"error": "invalid_periodId"}), 400
    if status not in ("taken", "not_taken"):
        return jsonify({"error": "invalid_log_status"}), 400
    if not isinstance(scheduled_date, str):
        return jsonify({"error": "invalid_log_date"}), 400
    try:
        date_value = datetime.strptime(scheduled_date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "invalid_log_date"}), 400
    if date_value.isoformat() != scheduled_date:
        return jsonify({"error": "invalid_log_date"}), 400

    user_id = user_id.strip()
    try:
        user_meds = get_user_medicines_collection()
        scheduled_meds = {
            document["medId"]
            for document in user_meds.find(
                {
                    "userId": user_id,
                    "medId": {"$in": med_ids},
                    "timesPerDay": period_id,
                },
                {"_id": 0, "medId": 1},
            )
        }
        if scheduled_meds != set(med_ids):
            return jsonify({"error": "scheduled_medicine_not_found"}), 404

        medicine_documents = get_medicines_collection().find(
            {
                "$or": [
                    {"_id": {"$in": med_ids}},
                    {"medId": {"$in": med_ids}},
                ]
            },
            {"_id": 1, "medId": 1, "medName": 1},
        )
        medicine_names = {
            str(document.get("medId") or document["_id"]): document["medName"]
            for document in medicine_documents
        }

        logs = get_user_medic_logs_collection()
        logs.create_index(
            [("userId", 1), ("medId", 1), ("date", 1), ("periodId", 1)],
            unique=True,
            partialFilterExpression={
                "userId": {"$type": "string"},
                "medId": {"$type": "string"},
                "date": {"$type": "string"},
                "periodId": {"$type": "int"},
            },
            name="user_medication_period_unique",
        )
        recorded_at = datetime.now(timezone.utc)
        for med_id in med_ids:
            logs.update_one(
                {
                    "userId": user_id,
                    "medId": med_id,
                    "date": scheduled_date,
                    "periodId": period_id,
                },
                {
                    "$set": {
                        "medName": medicine_names.get(med_id, med_id),
                        "status": status,
                        "recordedAt": recorded_at,
                    }
                },
                upsert=True,
            )
        return jsonify(
            {
                "message": "successful",
                "date": scheduled_date,
                "periodId": period_id,
                "status": status,
                "medIds": med_ids,
            }
        )
    except RuntimeError:
        current_app.logger.error("MONGODB_URI is not configured.")
        return jsonify({"error": "database_not_configured"}), 503
    except PyMongoError:
        current_app.logger.error("MongoDB request failed while recording medication status.")
        return jsonify({"error": "database_unavailable"}), 503


@user_medicines.get("/user/med/log")
def list_medication_logs():
    user_id = request.args.get("user_id")
    if not isinstance(user_id, str) or not user_id.strip():
        return jsonify({"error": "user_id_is_required"}), 400

    try:
        documents = list(
            get_user_medic_logs_collection().find(
                {"userId": user_id.strip()},
                {
                    "_id": 0,
                    "medId": 1,
                    "medName": 1,
                    "med_name": 1,
                    "date": 1,
                    "status": 1,
                    "periodId": 1,
                },
            ).sort([("date", -1), ("periodId", -1)])
        )
        missing_med_ids = {
            document["medId"]
            for document in documents
            if isinstance(document.get("medId"), str)
            and not isinstance(
                document.get("medName") or document.get("med_name"), str
            )
        }
        medicine_names = {}
        if missing_med_ids:
            medicine_documents = get_medicines_collection().find(
                {
                    "$or": [
                        {"_id": {"$in": list(missing_med_ids)}},
                        {"medId": {"$in": list(missing_med_ids)}},
                    ]
                },
                {"_id": 1, "medId": 1, "medName": 1},
            )
            medicine_names = {
                str(document.get("medId") or document["_id"]): document["medName"]
                for document in medicine_documents
            }

        records = []
        for document in documents:
            med_id = document.get("medId")
            med_name = document.get("medName") or document.get("med_name")
            if not isinstance(med_name, str):
                med_name = medicine_names.get(med_id, "ไม่พบข้อมูลยา")
            raw_date = document.get("date")
            if isinstance(raw_date, datetime):
                record_date = raw_date.date().isoformat()
            elif isinstance(raw_date, date):
                record_date = raw_date.isoformat()
            else:
                record_date = raw_date

            records.append(
                {
                    "medName": med_name,
                    "date": record_date,
                    "status": document.get("status"),
                    "periodId": document.get("periodId"),
                }
            )
        return jsonify(records)
    except RuntimeError:
        current_app.logger.error("MONGODB_URI is not configured.")
        return jsonify({"error": "database_not_configured"}), 503
    except PyMongoError:
        current_app.logger.error("MongoDB request failed while listing medication logs.")
        return jsonify({"error": "database_unavailable"}), 503
