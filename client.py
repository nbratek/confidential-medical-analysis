import tenseal as ts
import requests

from data_parser import (
    get_glucose,
    get_bmi,
    get_blood_pressure
)



# 1. metoda pomocnicza do załadowania danych z limitem i filtrem
def load_values(loader, limit=100):
    values = [v for v in loader() if v is not None][:limit]
    if not values:
        raise ValueError("Brak danych dla wybranej metryki!")
    return values


# 2. metoda pomocnicza do stworzenia kontekstu HE
def make_context():
    ctx = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )
    ctx.global_scale = 2 ** 40
    ctx.generate_galois_keys()
    return ctx


# 3. metoda pomocnicza do wysyłki pojedynczej metryki do serwera
def post_single(endpoint, enc_bytes, context_bytes, context, n):
    # wysyłka do serwera
    try:
        response = requests.post(
            "http://127.0.0.1:5000/" + endpoint,
            files={"vector": ("vector.bin", enc_bytes), "context": ("context.bin", context_bytes)},
            data={"length": str(n)},
            timeout=30
        )
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Nie można połączyć z serwerem. Czy Flask działa?")

    # walidacja odpowiedzi
    if response.status_code != 200:
        print("Błąd serwera:", response.status_code)
        print(response.text)
        raise RuntimeError("Serwer zwrócił błąd")
        
    # odbiór i zwrot wyniku (CKKS)
    try:
        result_enc = ts.ckks_vector_from(context, response.content)
        return result_enc.decrypt()[0]
    except Exception as e:
        print("RAW RESPONSE (debug):", response.content[:200])
        raise RuntimeError(f"Błąd dekodowania CKKS: {e}")


# 4. obsługa poszczególnych metryk
def calculate_mean(enc_bytes, context_bytes, context, n):
    result = post_single("compute_mean", enc_bytes, context_bytes, context, n)
    print(f" == Mean = {result:.4f} \n")


def calculate_sum(enc_bytes, context_bytes, context, n):
    result = post_single("compute_sum", enc_bytes, context_bytes, context, n)
    print(f" == Sum = {result:.4f} \n")


def calculate_root_mean_square(enc_bytes, context_bytes, context, n):
    result = post_single("compute_sum_of_squares", enc_bytes, context_bytes, context, n)
    rms = (result / n) ** 0.5
    print(f" == Root Mean Square = {rms:.4f} \n")


def calculate_variance(enc_bytes, context_bytes, context, n):
    enc_sum = post_single("compute_sum", enc_bytes, context_bytes, context, n)
    enc_sum_of_squares = post_single("compute_sum_of_squares", enc_bytes, context_bytes, context, n)
    variance = (enc_sum_of_squares / n) - (enc_sum / n) ** 2
    print(f" == Variance = {variance:.4f} \n")


# dostępne metryki do wyboru
AVAILABLE_METRICS = {
    "1": ("Mean", calculate_mean),
    "2": ("Sum", calculate_sum),
    "3": ("Root Mean Square", calculate_root_mean_square),
    "4": ("Variance", calculate_variance)
}


# dostępne dane do wyboru
AVAILABLE_DATA = {
    "1": ("glucose", get_glucose),
    "2": ("bmi", get_bmi),
    "3": ("bp", get_blood_pressure)
}


def main():
    # 1. wybór typu danych do analizy
    print("Select data to analyze:")
    for k, (name, _) in AVAILABLE_DATA.items():
        print(f" * {k} - {name}")
    dk = input("> ").strip().lower()
    if dk not in AVAILABLE_DATA:
        print(" ! Invalid choice.")
        return

    # 2. załadowanie danych
    label, loader = AVAILABLE_DATA[dk]
    values = load_values(loader)
    n = len(values)
    print(f"Loaded {n} samples for data = {label}")

    # 3. utworzenie kontekstu HE i zaszyfrowanie wektora
    context = make_context()
    enc_vec = ts.ckks_vector(context, values)
    context_bytes = context.serialize(save_secret_key=False)
    enc_bytes = enc_vec.serialize()

    # 4. pętla zapytań
    while True:
        # 5. wybór metryk do obliczenia
        print("Select metric to compute:")
        for k, (name, _) in AVAILABLE_METRICS.items():
            print(f" * {k} - {name}")
        print(" * q - Exit")

        # 6. odczyt wyboru
        choice = input("> ").strip().lower()

        # 7. obsługa wyboru
        if choice == "q":
            break
        selected = choice.strip()
        if selected not in AVAILABLE_METRICS:
            print(" ! Invalid choice.")
            continue

        # 8. wykonanie obliczeń dla wybranej metryki
        print()
        desc, handler = AVAILABLE_METRICS[selected]
        print(f" Calculating {desc}...")
        handler(enc_bytes, context_bytes, context, n)


if __name__ == "__main__":
    main()