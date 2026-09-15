from datetime import date

import db
from models import appointment

TEST_DATE = date(2099, 1, 1)
TEST_TIME = "08:00"


def _delete_test_appointment(appointment_id):
    connection = db.get_connection()
    try:
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM APPOINTMENTS WHERE ID = :id", id=appointment_id)
            connection.commit()
        finally:
            cursor.close()
    finally:
        connection.close()


def main():
    print("1) Inserindo agendamento de teste...")
    created = appointment.create_appointment(
        patient_name="Paciente Teste",
        patient_phone="11999999999",
        appointment_date=TEST_DATE,
        appointment_time=TEST_TIME,
    )
    print("   Criado:", created)

    try:
        print("\n2) Consultando agendamentos na data de teste...")
        results = appointment.list_appointments(TEST_DATE)
        for row in results:
            print("  ", row)
    finally:
        print(f"\n3) Removendo agendamento de teste (ID={created['id']})...")
        _delete_test_appointment(created["id"])
        print("   Removido.")

    print("\n4) Confirmando que nao sobrou registro de teste...")
    remaining = appointment.list_appointments(TEST_DATE)
    if remaining:
        print("   ATENCAO: ainda ha registros na data de teste:", remaining)
    else:
        print("   OK: nenhum agendamento restante na data de teste.")


if __name__ == "__main__":
    main()
