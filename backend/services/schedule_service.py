from datetime import date, datetime
from zoneinfo import ZoneInfo

import oracledb

from models import appointment
from services import holidays_service

TIMEZONE = ZoneInfo("America/Sao_Paulo")
BUSINESS_START_HOUR = 8
BUSINESS_END_HOUR = 18
PATIENT_NAME_MAX_LENGTH = 150
PATIENT_PHONE_MAX_LENGTH = 20


class SlotUnavailableError(Exception):
    """Data/horario valido no formato, mas indisponivel para agendamento."""


HolidaysUnavailableError = holidays_service.HolidaysUnavailableError


def parse_date(date_str):
    try:
        return date.fromisoformat(date_str)
    except (TypeError, ValueError):
        raise ValueError(f"Data invalida: {date_str!r}. Use o formato YYYY-MM-DD.")


def is_weekend(a_date):
    return a_date.weekday() >= 5  # 5 = sabado, 6 = domingo


def is_past_date(a_date):
    today = datetime.now(TIMEZONE).date()
    return a_date < today


def generate_business_hours():
    return [f"{hour:02d}:00" for hour in range(BUSINESS_START_HOUR, BUSINESS_END_HOUR)]


def parse_time(time_str):
    if time_str not in generate_business_hours():
        raise ValueError(
            f"Horario invalido: {time_str!r}. Deve ser um dos horarios entre "
            f"{BUSINESS_START_HOUR:02d}:00 e {BUSINESS_END_HOUR - 1:02d}:00, em intervalos de 1 hora."
        )
    return time_str


def get_booked_times(a_date):
    return {row["appointment_time"] for row in appointment.list_appointments(a_date)}


def get_available_slots(a_date):
    booked = get_booked_times(a_date)
    return [slot for slot in generate_business_hours() if slot not in booked]


def get_availability(date_str):
    a_date = parse_date(date_str)

    if is_past_date(a_date):
        return {"date": date_str, "available": False, "reason": "Data no passado", "slots": []}

    if is_weekend(a_date):
        return {"date": date_str, "available": False, "reason": "Fim de semana", "slots": []}

    holiday_name = holidays_service.get_holiday_name(a_date)
    if holiday_name:
        return {"date": date_str, "available": False, "reason": f"Feriado: {holiday_name}", "slots": []}

    return {"date": date_str, "available": True, "reason": None, "slots": get_available_slots(a_date)}


def book_appointment(patient_name, patient_phone, date_str, time_str):
    if not patient_name or not str(patient_name).strip():
        raise ValueError("O campo 'patient_name' e obrigatorio.")

    if len(str(patient_name).strip()) > PATIENT_NAME_MAX_LENGTH:
        raise ValueError(f"O campo 'patient_name' deve ter no maximo {PATIENT_NAME_MAX_LENGTH} caracteres.")

    if patient_phone is not None and len(str(patient_phone).strip()) > PATIENT_PHONE_MAX_LENGTH:
        raise ValueError(f"O campo 'patient_phone' deve ter no maximo {PATIENT_PHONE_MAX_LENGTH} caracteres.")

    a_date = parse_date(date_str)
    parse_time(time_str)

    if is_past_date(a_date):
        raise SlotUnavailableError("Nao e possivel agendar em uma data no passado.")

    if is_weekend(a_date):
        raise SlotUnavailableError("Nao e possivel agendar aos sabados ou domingos.")

    holiday_name = holidays_service.get_holiday_name(a_date)
    if holiday_name:
        raise SlotUnavailableError(f"Nao e possivel agendar em feriado ({holiday_name}).")

    if time_str in get_booked_times(a_date):
        raise SlotUnavailableError("Horario ja ocupado.")

    try:
        return appointment.create_appointment(
            patient_name=patient_name.strip(),
            patient_phone=patient_phone,
            appointment_date=a_date,
            appointment_time=time_str,
        )
    except oracledb.IntegrityError as exc:
        raise SlotUnavailableError("Horario ja ocupado.") from exc


def list_appointments(date_str=None):
    if date_str is None:
        return appointment.list_appointments()

    a_date = parse_date(date_str)
    return appointment.list_appointments(a_date)
