from flask import Blueprint, jsonify, request

from services import schedule_service

available_bp = Blueprint("available", __name__)


@available_bp.route("/available", methods=["GET"])
def get_available():
    date_str = request.args.get("date")

    try:
        availability = schedule_service.get_availability(date_str)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except schedule_service.HolidaysUnavailableError as exc:
        return jsonify({"error": str(exc)}), 503

    return jsonify(availability), 200
