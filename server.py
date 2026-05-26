from flask import Flask, request
import tenseal as ts

app = Flask(__name__)

@app.route("/compute_mean", methods=["POST"])
def compute_mean():

    # =========================
    # 1. ODBIÓR DANYCH
    # =========================
    vector_bytes = request.files["vector"].read()
    context_bytes = request.files["context"].read()

    length = int(request.form["length"])  # <- KLUCZOWE

    # =========================
    # 2. ODTWORZENIE KONTEKSTU
    # =========================
    context = ts.context_from(context_bytes)

    # =========================
    # 3. ODTWORZENIE WEKTORA
    # =========================
    enc_vector = ts.ckks_vector_from(context, vector_bytes)

    # =========================
    # 4. HOMOMORFICZNE LICZENIE
    # =========================
    enc_sum = enc_vector.sum()
    enc_mean = enc_sum * (1 / length)

    # =========================
    # 5. ZWROT ZASZYFROWANEGO WYNIKU
    # =========================
    return enc_mean.serialize()


if __name__ == "__main__":
    app.run(port=5000, debug=True)