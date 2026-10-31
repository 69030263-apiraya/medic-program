import uuid

from flask import Blueprint, current_app, jsonify
from pymongo.errors import DuplicateKeyError, PyMongoError

from .database import get_medicine_types_collection
from .request_helpers import get_json_payload

medicine_type = Blueprint("medicine_type", __name__)


@medicine_type.post("/med/type")
def create_medicine_type():
    payload, error_response = get_json_payload()
    if error_response:
        return error_response

    type_name = payload.get("medTypeName")
    if not isinstance(type_name, str) or not type_name.strip():
        return jsonify({"error": "medTypeName_is_required"}), 400

    type_name = type_name.strip()
    try:
        types = get_medicine_types_collection()
        types.create_index("medTypeName", unique=True)
        if types.find_one({"medTypeName": type_name}, {"_id": 1}) is not None:
            return jsonify({"error": "medicine_type_already_exists"}), 409

        medicine_type_data = {
            "medTypeId": str(uuid.uuid4()),
            "medTypeName": type_name,
        }
        types.insert_one(medicine_type_data)
        return jsonify(medicine_type_data), 201
    except DuplicateKeyError:
        return jsonify({"error": "medicine_type_already_exists"}), 409
    except RuntimeError:
        current_app.logger.error("MONGODB_URI is not configured.")
        return jsonify({"error": "database_not_configured"}), 503
    except PyMongoError:
        current_app.logger.error("MongoDB request failed while creating a medicine type.")
        return jsonify({"error": "database_unavailable"}), 503


@medicine_type.get("/med/type")
def list_medicine_types():
    try:
        types = get_medicine_types_collection()
        documents = types.find({}, {"_id": 0, "medTypeId": 1, "medTypeName": 1})
        return jsonify(
            [
                {
                    "medTypeId": document["medTypeId"],
                    "medTypeName": document["medTypeName"],
                }
                for document in documents
            ]
        )
    except RuntimeError:
        current_app.logger.error("MONGODB_URI is not configured.")
        return jsonify({"error": "database_not_configured"}), 503
    except PyMongoError:
        current_app.logger.error("MongoDB request failed while listing medicine types.")
        return jsonify({"error": "database_unavailable"}), 503


@medicine_type.delete("/med/type")
def delete_medicine_type():
    payload, error_response = get_json_payload()
    if error_response:
        return error_response

    type_id = payload.get("medTypeId")
    if not isinstance(type_id, str) or not type_id.strip():
        return jsonify({"error": "medTypeId_is_required"}), 400

    try:
        result = get_medicine_types_collection().delete_one(
            {"medTypeId": type_id.strip()}
        )
        if result.deleted_count == 0:
            return jsonify({"error": "medicine_type_not_found"}), 404

        return jsonify({"message": "successful", "medTypeId": type_id.strip()})
    except RuntimeError:
        current_app.logger.error("MONGODB_URI is not configured.")
        return jsonify({"error": "database_not_configured"}), 503
    except PyMongoError:
        current_app.logger.error("MongoDB request failed while deleting a medicine type.")
        return jsonify({"error": "database_unavailable"}), 503
