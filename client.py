import tenseal as ts
import requests

from data_parser import (
    get_glucose,
    get_bmi,
    get_blood_pressure
)

# =========================
# 1. WYBÓR METRYKI
# =========================

METRIC = "glucose"   # glucose | bmi | bp

if METRIC == "glucose":
    values = get_glucose()
elif METRIC == "bmi":
    values = get_bmi()
elif METRIC == "bp":
    values = get_blood_pressure()
else:
    raise ValueError("Unknown metric")

# filtr + limit
values = [v for v in values if v is not None]
values = values[:100]

if len(values) == 0:
    raise ValueError("Brak danych dla wybranej metryki!")

print(f"Liczba próbek ({METRIC}): {len(values)}")


# =========================
# 2. KONTEKST HE
# =========================

context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60]
)

context.global_scale = 2**40
context.generate_galois_keys()


# =========================
# 3. SZYFROWANIE
# =========================

enc_vector = ts.ckks_vector(context, values)

enc_bytes = enc_vector.serialize()
context_bytes = context.serialize(save_secret_key=False)


# =========================
# 4. WYSYŁKA DO SERWERA
# =========================

files = {
    "vector": ("vector.bin", enc_bytes),
    "context": ("context.bin", context_bytes)
}

data = {
    "length": str(len(values))
}

try:
    response = requests.post(
        "http://127.0.0.1:5000/compute_mean",
        files=files,
        data=data,
        timeout=30
    )
except requests.exceptions.ConnectionError:
    raise RuntimeError("Nie można połączyć z serwerem. Czy Flask działa?")


# =========================
# 5. WALIDACJA ODPOWIEDZI
# =========================

if response.status_code != 200:
    print("Błąd serwera:", response.status_code)
    print(response.text)
    raise RuntimeError("Serwer zwrócił błąd")


# =========================
# 6. ODBIÓR WYNIKU (CKKS)
# =========================

try:
    result_enc = ts.ckks_vector_from(context, response.content)
    result = result_enc.decrypt()[0]
except Exception as e:
    print("RAW RESPONSE (debug):", response.content[:200])
    raise RuntimeError(f"Błąd dekodowania CKKS: {e}")


# =========================
# 7. OUTPUT
# =========================

print(f"\nŚrednia ({METRIC}): {result:.4f}")