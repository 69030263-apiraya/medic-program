import uuid

from flask import Blueprint, current_app, jsonify, request
from pymongo.errors import PyMongoError

from .database import get_medicine_types_collection, get_medicines_collection
from .request_helpers import get_json_payload

medicines = Blueprint("medicines", __name__)


@medicines.post("/med")
def create_medicine():
    payload, error_response = get_json_payload()
    if error_response:
        return error_response

    med_name = payload.get("medName")
    med_type_id = payload.get("medTypeId")
    unit_name = payload.get("unitName")
    bud = payload.get("BUD")

    if not isinstance(med_name, str) or not med_name.strip():
        return jsonify({"error": "medName_is_required"}), 400
    if not isinstance(med_type_id, str) or not med_type_id.strip():
        return jsonify({"error": "medTypeId_is_required"}), 400
    if not isinstance(unit_name, str) or not unit_name.strip():
        return jsonify({"error": "unitName_is_required"}), 400
    if not isinstance(bud, int) or isinstance(bud, bool) or bud < 0:
        return jsonify(
            {"error": "invalid_BUD", "message": "BUD must be a non-negative integer number of days."}
        ), 400

    med_name = med_name.strip()
    med_type_id = med_type_id.strip()
    unit_name = unit_name.strip()

    try:
        types = get_medicine_types_collection()
        med_type = types.find_one(
            {
                "$or": [
                    {"_id": med_type_id},
                    {"medTypeId": med_type_id},
                ]
            },
            {"_id": 1},
        )
        if med_type is None:
            return jsonify({"error": "medicine_type_not_found"}), 404

        med_id = str(uuid.uuid4())
        get_medicines_collection().insert_one(
            {
                "_id": med_id,
                "medName": med_name,
                "medTypeId": med_type_id,
                "unitName": unit_name,
                "BUD": bud,
            }
        )
        return jsonify(
            {
                "medId": med_id,
                "medName": med_name,
                "medTypeId": med_type_id,
                "unitName": unit_name,
                "BUD": bud,
            }
        ), 201
    except RuntimeError:
        current_app.logger.error("MONGODB_URI is not configured.")
        return jsonify({"error": "database_not_configured"}), 503
    except PyMongoError:
        current_app.logger.error("MongoDB request failed while creating a medicine.")
        return jsonify({"error": "database_unavailable"}), 503


@medicines.get("/med")
def list_medicines():
    type_id = request.args.get("type")
    query = {}
    if type_id is not None:
        if not type_id.strip():
            return jsonify({"error": "type_must_not_be_empty"}), 400
        query["medTypeId"] = type_id.strip()

    try:
        documents = get_medicines_collection().find(
            query,
            {"_id": 1, "medId": 1, "medName": 1, "medTypeId": 1, "unitName": 1, "BUD": 1},
        )
        return jsonify(
            [
                {
                    "medId": str(document.get("medId") or document["_id"]),
                    "medName": document["medName"],
                    "medTypeId": document["medTypeId"],
                    "unitName": document["unitName"],
                    "BUD": document["BUD"],
                }
                for document in documents
            ]
        )
    except RuntimeError:
        current_app.logger.error("MONGODB_URI is not configured.")
        return jsonify({"error": "database_not_configured"}), 503
    except PyMongoError:
        current_app.logger.error("MongoDB request failed while listing medicines.")
        return jsonify({"error": "database_unavailable"}), 503


@medicines.delete("/med")
def delete_medicine():
    payload, error_response = get_json_payload()
    if error_response:
        return error_response

    med_id = payload.get("medId")
    if not isinstance(med_id, str) or not med_id.strip():
        return jsonify({"error": "medId_is_required"}), 400

    med_id = med_id.strip()
    try:
        result = get_medicines_collection().delete_one(
            {"$or": [{"_id": med_id}, {"medId": med_id}]}
        )
        if result.deleted_count == 0:
            return jsonify({"error": "medicine_not_found"}), 404

        return jsonify({"message": "successful", "medId": med_id})
    except RuntimeError:
        current_app.logger.error("MONGODB_URI is not configured.")
        return jsonify({"error": "database_not_configured"}), 503
    except PyMongoError:
        current_app.logger.error("MongoDB request failed while deleting a medicine.")
        return jsonify({"error": "database_unavailable"}), 503
