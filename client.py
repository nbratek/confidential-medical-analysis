import tenseal as ts
import requests

from data_parser import list_metrics, get_metric


# metoda pomocnicza do załadowania danych z limitem i filtrem
def load_values(metric_name, limit=100):
    values = [v for v in get_metric(metric_name) if v is not None][:limit]
    if not values:
        raise ValueError(f"No data for metric: {metric_name}")
    return values


# metoda pomocnicza do stworzenia kontekstu HE
def make_context():
    ctx = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )
    ctx.global_scale = 2 ** 40
    ctx.generate_galois_keys()
    return ctx


# metoda pomocnicza do wysyłki pojedynczej metryki do serwera
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
        raise RuntimeError("Cannot connect to server. Is Flask running?")

    # walidacja odpowiedzi
    if response.status_code != 200:
        print("Server error:", response.status_code)
        print(response.text)
        raise RuntimeError("Server returned an error")

    # odbiór i zwrot wyniku (CKKS)
    try:
        result_enc = ts.ckks_vector_from(context, response.content)
        return result_enc.decrypt()[0]
    except Exception as e:
        print("Raw response:", response.content[:200])
        raise RuntimeError(f"CKKS decoding error: {e}")


# obsługa poszczególnych metryk
def calculate_mean(enc_bytes, context_bytes, context, n):
    result = post_single("compute_mean", enc_bytes, context_bytes, context, n)
    print(f"    Mean {result:.4f} \n")


def calculate_sum(enc_bytes, context_bytes, context, n):
    result = post_single("compute_sum", enc_bytes, context_bytes, context, n)
    print(f"    Sum {result:.4f} \n")


def calculate_root_mean_square(enc_bytes, context_bytes, context, n):
    result = post_single("compute_sum_of_squares", enc_bytes, context_bytes, context, n)
    rms = (result / n) ** 0.5
    print(f"    Root Mean Square  {rms:.4f} \n")


def calculate_variance(enc_bytes, context_bytes, context, n):
    enc_sum = post_single("compute_sum", enc_bytes, context_bytes, context, n)
    enc_sum_of_squares = post_single("compute_sum_of_squares", enc_bytes, context_bytes, context, n)
    variance = (enc_sum_of_squares / n) - (enc_sum / n) ** 2
    print(f"    Variance  {variance:.4f} \n")


# dostępne statystyki do obliczenia
AVAILABLE_METRICS = {
    "1": ("Mean", calculate_mean),
    "2": ("Sum", calculate_sum),
    "3": ("Root Mean Square", calculate_root_mean_square),
    "4": ("Variance", calculate_variance)
}


def main():
    # lista metryk z observations.csv
    metrics = list_metrics()
    if not metrics:
        print("No metrics available in data/observations.csv")
        return

    data_options = sorted(metrics.keys())
    # wybór typu danych
    print("Select data to analyze:")
    for i, name in enumerate(data_options, start=1):
        print(f" * {i} - {name}")

    choice = input("> ").strip()
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(data_options):
        print("Invalid choice.")
        return

    chosen_metric = data_options[int(choice) - 1]
    # załadowanie danych
    values = load_values(chosen_metric)
    n = len(values)
    print(f"\nLoaded {n} samples for: {chosen_metric}")

    # utworzenie kontekstu HE i zaszyfrowanie wektora
    context = make_context()
    enc_vec = ts.ckks_vector(context, values)
    context_bytes = context.serialize(save_secret_key=False)
    enc_bytes = enc_vec.serialize()

    # pętla zapytań o statystyki
    stat_options = list(AVAILABLE_METRICS.values())
    while True:
        print()
        print("Select statistic to compute:")
        for i, (label, _) in enumerate(stat_options, start=1):
            print(f" * {i} - {label}")
        print(" * q - Exit")

        choice = input("> ").strip().lower()
        if choice == "q":
            break

        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(stat_options):
            print("Invalid choice.")
            continue

        # wykonanie obliczeń dla wybranej metryki
        label, handler = stat_options[int(choice) - 1]
        print(f"\n  Calculating {label}: \n")
        handler(enc_bytes, context_bytes, context, n)


if __name__ == "__main__":
    main()