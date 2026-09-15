from datetime import date

import requests

import config

_cache = {}


class HolidaysUnavailableError(Exception):
    """Nao foi possivel consultar a API de feriados (Nager)."""


def get_holidays(year):
    if year not in _cache:
        try:
            response = requests.get(f"{config.NAGER_API_BASE}/PublicHolidays/{year}/BR", timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            raise HolidaysUnavailableError(
                "Nao foi possivel verificar feriados no momento. Tente novamente em instantes."
            ) from exc

        _cache[year] = {
            date.fromisoformat(item["date"]): item["localName"] for item in response.json()
        }
    return _cache[year]


def get_holiday_name(a_date):
    return get_holidays(a_date.year).get(a_date)
