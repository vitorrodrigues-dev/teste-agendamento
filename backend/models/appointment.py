import db


def _row_to_dict(cursor, row):
    if row is None:
        return None
    columns = [col[0].lower() for col in cursor.description]
    return dict(zip(columns, row))


def create_appointment(patient_name, patient_phone, appointment_date, appointment_time):
    connection = db.get_connection()
    try:
        cursor = connection.cursor()
        try:
            new_id = cursor.var(int)
            cursor.execute(
                """
                INSERT INTO APPOINTMENTS
                    (PATIENT_NAME, PATIENT_PHONE, APPOINTMENT_DATE, APPOINTMENT_TIME)
                VALUES
                    (:patient_name, :patient_phone, :appointment_date, :appointment_time)
                RETURNING ID INTO :new_id
                """,
                patient_name=patient_name,
                patient_phone=patient_phone,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                new_id=new_id,
            )
            connection.commit()

            cursor.execute("SELECT * FROM APPOINTMENTS WHERE ID = :id", id=int(new_id.getvalue()[0]))
            return _row_to_dict(cursor, cursor.fetchone())
        finally:
            cursor.close()
    finally:
        connection.close()


def list_appointments(appointment_date=None):
    connection = db.get_connection()
    try:
        cursor = connection.cursor()
        try:
            if appointment_date is not None:
                cursor.execute(
                    """
                    SELECT * FROM APPOINTMENTS
                    WHERE APPOINTMENT_DATE = :appointment_date
                    ORDER BY APPOINTMENT_TIME
                    """,
                    appointment_date=appointment_date,
                )
            else:
                cursor.execute("SELECT * FROM APPOINTMENTS ORDER BY APPOINTMENT_DATE, APPOINTMENT_TIME")

            return [_row_to_dict(cursor, row) for row in cursor.fetchall()]
        finally:
            cursor.close()
    finally:
        connection.close()
