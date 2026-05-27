from flask import Flask, render_template, request, jsonify
import numpy as np
from scipy.optimize import linprog

app = Flask(__name__)

# ==========================================================
# HALAMAN UTAMA
# ==========================================================
@app.route("/")
def home():
    return render_template("index.html")

# ==========================================================
# SOLVER GOAL PROGRAMMING
# ==========================================================
@app.route("/solve", methods=["POST"])
def solve():

    data = request.json

    coef = data["coef"]
    rhs = data["rhs"]
    objectives = data["objectives"]
    n_var = data["n_var"]

    n_goal = len(rhs)

    total_var = n_var + (2 * n_goal)

    c = [0] * total_var

    A_eq = []
    b_eq = []

    for i in range(n_goal):

        row = [0] * total_var

        # variabel keputusan
        for j in range(n_var):
            row[j] = coef[i][j]

        # deviasi
        dm = n_var + (2 * i)
        dp = n_var + (2 * i) + 1

        row[dm] = 1
        row[dp] = -1

        A_eq.append(row)

        b_eq.append(rhs[i])

        # objective
        typ = objectives[i].lower()

        if typ == "m":
            c[dm] = 1

        elif typ == "p":
            c[dp] = 1

        elif typ == "b":
            c[dm] = 1
            c[dp] = 1

    bounds = [(0, None)] * total_var

    result = linprog(
        c=c,
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=bounds,
        method="highs"
    )

    if result.success:

        return jsonify({
            "status": 0,
            "z": float(result.fun),
            "x": result.x.tolist()
        })

    return jsonify({
        "status": 1,
        "message": result.message
    })

# ==========================================================
# RUN
# ==========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)