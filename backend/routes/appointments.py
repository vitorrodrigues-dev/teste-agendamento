from flask import Blueprint, jsonify, request

from services import schedule_service

appointments_bp = Blueprint("appointments", __name__)


def _serialize_appointment(row):
    return {
        "id": row["id"],
        "patient_name": row["patient_name"],
        "patient_phone": row["patient_phone"],
        "appointment_date": row["appointment_date"].strftime("%Y-%m-%d"),
        "appointment_time": row["appointment_time"],
        "status": row["status"],
        "created_at": row["created_at"].isoformat(),
    }


@appointments_bp.route("/appointments", methods=["POST"])
def post_appointment():
    payload = request.get_json(silent=True) or {}

    try:
        created = schedule_service.book_appointment(
            patient_name=payload.get("patient_name"),
            patient_phone=payload.get("patient_phone"),
            date_str=payload.get("appointment_date"),
            time_str=payload.get("appointment_time"),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except schedule_service.SlotUnavailableError as exc:
        return jsonify({"error": str(exc)}), 409
    except schedule_service.HolidaysUnavailableError as exc:
        return jsonify({"error": str(exc)}), 503

    return jsonify(_serialize_appointment(created)), 201


@appointments_bp.route("/appointments", methods=["GET"])
def get_appointments():
    date_str = request.args.get("date")

    try:
        appointments = schedule_service.list_appointments(date_str)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify([_serialize_appointment(row) for row in appointments]), 200
