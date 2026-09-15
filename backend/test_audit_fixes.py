import requests

import app as app_module
import config
from services import holidays_service


def main():
    client = app_module.app.test_client()

    print("== FLASK_DEBUG efetivo ==")
    print("config.FLASK_DEBUG =", config.FLASK_DEBUG)
    print("(app.debug so reflete isso quando o servidor sobe via app.run(), nao via test_client)")

    print("\n== nome > 150 caracteres (POST /appointments) ==")
    resp = client.post(
        "/appointments",
        json={
            "patient_name": "A" * 151,
            "appointment_date": "2026-09-17",
            "appointment_time": "09:00",
        },
    )
    print(resp.status_code, resp.get_json())
    assert resp.status_code == 400

    print("\n== telefone > 20 caracteres (POST /appointments) ==")
    resp = client.post(
        "/appointments",
        json={
            "patient_name": "Nome Valido",
            "patient_phone": "1" * 21,
            "appointment_date": "2026-09-17",
            "appointment_time": "09:00",
        },
    )
    print(resp.status_code, resp.get_json())
    assert resp.status_code == 400

    print("\n== nome com exatamente 150 caracteres (limite, deve passar da validacao de tamanho) ==")
    resp = client.post(
        "/appointments",
        json={
            "patient_name": "B" * 150,
            "appointment_date": "2026-09-17",
            "appointment_time": "09:00",
        },
    )
    print(resp.status_code, resp.get_json())
    assert resp.status_code == 201, "nome com 150 caracteres deveria ser aceito"

    print("\n== Nager indisponivel (mock, sem derrubar a API real) ==")
    holidays_service._cache.clear()
    original_get = requests.get

    def broken_get(*args, **kwargs):
        raise requests.exceptions.ConnectionError("Falha de rede simulada para o teste")

    requests.get = broken_get
    try:
        resp = client.get("/available?date=2031-05-20")
        print("GET /available com Nager fora do ar:", resp.status_code, resp.get_json())
        assert resp.status_code == 503

        resp = client.post(
            "/appointments",
            json={
                "patient_name": "Nome Valido",
                "appointment_date": "2031-05-20",
                "appointment_time": "10:00",
            },
        )
        print("POST /appointments com Nager fora do ar:", resp.status_code, resp.get_json())
        assert resp.status_code == 503
    finally:
        requests.get = original_get
        holidays_service._cache.clear()

    print("\nTodos os testes de auditoria passaram.")


if __name__ == "__main__":
    main()
