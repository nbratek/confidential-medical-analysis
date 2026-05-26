import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.join(BASE_DIR, "synthea", "output", "fhir")


# =========================
# HELPERS
# =========================

def _load_json_files():
    """Ładuje wszystkie pliki FHIR JSON"""
    for file in os.listdir(FOLDER):
        if not file.endswith(".json"):
            continue

        path = os.path.join(FOLDER, file)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        yield data


def _extract_observations():
    """Zwraca wszystkie Observation z FHIR"""
    for data in _load_json_files():
        if "entry" not in data:
            continue

        for entry in data["entry"]:
            resource = entry.get("resource", {})

            if resource.get("resourceType") == "Observation":
                yield resource


def _get_numeric_value(obs):
    """Wyciąga wartość liczbową"""
    return obs.get("valueQuantity", {}).get("value")


def _matches_code(obs, keywords):
    """Sprawdza czy Observation dotyczy danego badania"""
    text = str(obs.get("code", {})).lower()
    return any(k.lower() in text for k in keywords)


# =========================
# PUBLIC FUNCTIONS
# =========================

def get_all_values():
    """Wszystkie wartości (fallback)"""
    values = []

    for obs in _extract_observations():
        v = _get_numeric_value(obs)
        if v is not None:
            values.append(v)

    return values


def get_glucose():
    """Glukoza we krwi"""
    values = []

    for obs in _extract_observations():
        if _matches_code(obs, ["glucose"]):
            v = _get_numeric_value(obs)
            if v is not None:
                values.append(v)

    return values


def get_bmi():
    """BMI"""
    values = []

    for obs in _extract_observations():
        if _matches_code(obs, ["bmi"]):
            v = _get_numeric_value(obs)
            if v is not None:
                values.append(v)

    return values


def get_blood_pressure():
    """Ciśnienie (MAP / systolic / diastolic - uproszczone)"""
    values = []

    for obs in _extract_observations():
        if _matches_code(obs, ["blood pressure", "systolic", "diastolic"]):
            v = _get_numeric_value(obs)
            if v is not None:
                values.append(v)

    return values