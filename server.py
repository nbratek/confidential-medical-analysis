from flask import Flask, request
import tenseal as ts

app = Flask(__name__)


def get_vector_and_length(request):
    # 1. odbiór danych
    vector_bytes = request.files["vector"].read()
    context_bytes = request.files["context"].read()

    length = int(request.form["length"])

    # 2. odtworzenie kontekstu
    context = ts.context_from(context_bytes)

    # 3. odtworzenie wektora
    enc_vector = ts.ckks_vector_from(context, vector_bytes)

    # 4. zwrócenie odtworzonych danych
    return enc_vector, length
    

@app.route("/compute_mean", methods=["POST"])
def compute_mean():
    # 1. odbiór danych
    enc_vector, length = get_vector_and_length(request)

    # 2. homomorficzne liczenie
    enc_sum = enc_vector.sum()
    enc_mean = enc_sum * (1 / length)

    # 3. zwrot zaszyfrowanego wyniku
    return enc_mean.serialize()


@app.route("/compute_sum", methods=["POST"])
def compute_sum():
    enc_vector, _ = get_vector_and_length(request)
    enc_sum = enc_vector.sum()
    return enc_sum.serialize()


@app.route("/compute_sum_of_squares", methods=["POST"])
def compute_sum_of_squares():
    enc_vector, _ = get_vector_and_length(request)
    enc_sum_sq = (enc_vector * enc_vector).sum()
    return enc_sum_sq.serialize()


@app.route("/compute_sum_of_products", methods=["POST"])
def compute_sum_of_products():
    # 1. odbiór danych
    vector_x_bytes = request.files["vector_x"].read()
    vector_y_bytes = request.files["vector_y"].read()
    context_bytes = request.files["context"].read()

    # 2. odtworzenie kontekstu
    context = ts.context_from(context_bytes)

    # 3. odtworzenie wektorów x i y
    enc_x_vector = ts.ckks_vector_from(context, vector_x_bytes)
    enc_y_vector = ts.ckks_vector_from(context, vector_y_bytes)

    # 4. homomorficzne liczenie
    enc_x_enc_y_sum = (enc_x_vector * enc_y_vector).sum()

    # 5. zwrot zaszyfrowanego wyniku
    return enc_x_enc_y_sum.serialize()


if __name__ == "__main__":
    app.run(port=5000, debug=True)