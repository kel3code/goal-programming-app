"""
ADVANCED GOAL PROGRAMMING GUI
======================================================
✔ PURE PYTHON DUAL REVISED SIMPLEX
✔ TANPA SCIPY
✔ TANPA LINPROG
✔ IMPORT EXCEL
✔ SAVE TXT / PDF / EXCEL
✔ FULL GUI
✔ FIXED 5 GOALS
✔ GOAL PROGRAMMING
======================================================
"""

# =====================================================
# IMPORT LIBRARY
# =====================================================

import tkinter as tk

from tkinter import messagebox
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText

import numpy as np
import pandas as pd

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Preformatted
)

from reportlab.lib.styles import getSampleStyleSheet

EPS = 1e-9


# =====================================================
# DUAL REVISED SIMPLEX SOLVER
# =====================================================

class DualRevisedSimplex:

    def __init__(self, c, A, b):

        self.c = c.astype(float)

        self.A = A.astype(float)

        self.b = b.astype(float)

        self.m, self.n = A.shape

        self.iterations = []

    # =================================================
    # SOLVE
    # =================================================

    def solve(self):

        # =================================================
        # INITIAL BASIS
        # gunakan variabel deviasi sebagai basis awal
        # =================================================

        basis = list(
            range(self.n - self.m, self.n)
        )

        non_basis = list(
            range(self.n - self.m)
        )

        iteration = 0

        while True:

            iteration += 1

            # =============================================
            # BASIS MATRIX
            # =============================================

            B = self.A[:, basis]

            try:

                B_inv = np.linalg.inv(B)

            except:

                raise Exception(
                    "Basis singular"
                )

            cb = self.c[basis]

            xb = B_inv @ self.b

            # =============================================
            # REDUCED COST
            # =============================================

            y = cb @ B_inv

            reduced = []

            for j in non_basis:

                val = self.c[j] - y @ self.A[:, j]

                reduced.append(val)

            reduced = np.array(reduced)

            # =============================================
            # SAVE ITERATION
            # =============================================

            self.iterations.append({
                "iter": iteration,
                "basis": basis.copy(),
                "xb": xb.copy(),
                "reduced": reduced.copy()
            })

            # =============================================
            # CEK OPTIMAL
            # =============================================

            if np.all(xb >= -EPS):

                x = np.zeros(self.n)

                for i, bi in enumerate(basis):

                    x[bi] = xb[i]

                z = self.c @ x

                return {
                    "x": x,
                    "fun": z,
                    "status": 0,
                    "iterations": self.iterations
                }

            # =============================================
            # PILIH LEAVING VARIABLE
            # =============================================

            leaving_row = np.argmin(xb)

            if xb[leaving_row] >= -EPS:

                raise Exception(
                    "Optimal"
                )

            # =============================================
            # DIRECTION
            # =============================================

            row = B_inv[leaving_row, :] @ self.A

            candidates = []

            for j_idx, j in enumerate(non_basis):

                if row[j] < -EPS:

                    ratio = reduced[j_idx] / (-row[j])

                    candidates.append(
                        (ratio, j_idx, j)
                    )

            if len(candidates) == 0:

                raise Exception(
                    "Model infeasible"
                )

            # =============================================
            # ENTERING VARIABLE
            # =============================================

            candidates.sort()

            _, enter_idx, enter_var = candidates[0]

            # =============================================
            # UPDATE BASIS
            # =============================================

            basis[leaving_row] = enter_var

            non_basis[enter_idx] = basis[leaving_row]

    # =================================================
    # END CLASS
    # =================================================


# =====================================================
# GUI
# =====================================================

class GoalProgrammingGUI:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "GOAL PROGRAMMING - DUAL REVISED SIMPLEX"
        )

        self.root.geometry("1500x950")

        # =================================================
        # CANVAS
        # =================================================

        self.canvas = tk.Canvas(root)

        self.scrollbar = tk.Scrollbar(
            root,
            orient="vertical",
            command=self.canvas.yview
        )

        self.scrollable_frame = tk.Frame(
            self.canvas
        )

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        self.canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.scrollbar.pack(
            side="right",
            fill="y"
        )

        self.canvas.bind_all(
            "<MouseWheel>",
            self._on_mousewheel
        )

        # =================================================
        # TITLE
        # =================================================

        tk.Label(
            self.scrollable_frame,
            text="ADVANCED GOAL PROGRAMMING SOLVER",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        # =================================================
        # INPUT
        # =================================================

        top = tk.Frame(
            self.scrollable_frame
        )

        top.pack(pady=10)

        tk.Label(
            top,
            text="Jumlah Variabel:",
            font=("Arial", 12, "bold")
        ).grid(row=0, column=0)

        self.entry_var = tk.Entry(
            top,
            width=10,
            font=("Arial", 12)
        )

        self.entry_var.grid(
            row=0,
            column=1
        )

        # =================================================
        # INFO
        # =================================================

        info = """
FORMAT INPUT

x1 x2 x3 ... rhs | objective

Contoh:

45 65 90 | m
23 11 40 | p
77 88 120 | b
12 44 55 | m
88 66 33 | p

m = minimize deviasi minus
p = minimize deviasi plus
b = minimize keduanya

GOAL TETAP:
1. ASET
2. LIABILITAS
3. EKUITAS
4. PENDAPATAN
5. BEBAN
"""

        tk.Label(
            self.scrollable_frame,
            text=info,
            justify="left",
            font=("Consolas", 11)
        ).pack(pady=10)

        # =================================================
        # INPUT TEXT
        # =================================================

        self.input_text = ScrolledText(
            self.scrollable_frame,
            width=150,
            height=20,
            font=("Consolas", 11)
        )

        self.input_text.pack(pady=10)

        # =================================================
        # BUTTONS
        # =================================================

        tk.Button(
            self.scrollable_frame,
            text="IMPORT EXCEL",
            command=self.load_excel,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            width=30,
            height=2
        ).pack(pady=5)

        tk.Button(
            self.scrollable_frame,
            text="SOLVE GOAL PROGRAMMING",
            command=self.solve,
            bg="#2196F3",
            fg="white",
            font=("Arial", 14, "bold"),
            width=35,
            height=2
        ).pack(pady=10)

        tk.Button(
            self.scrollable_frame,
            text="SAVE RESULT",
            command=self.save_result,
            bg="#FF9800",
            fg="white",
            font=("Arial", 12, "bold"),
            width=30,
            height=2
        ).pack(pady=5)

        # =================================================
        # RESULT
        # =================================================

        self.result_text = ScrolledText(
            self.scrollable_frame,
            width=170,
            height=35,
            font=("Consolas", 10)
        )

        self.result_text.pack(
            pady=10
        )

    # =================================================
    # SCROLL
    # =================================================

    def _on_mousewheel(self, event):

        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    # =================================================
    # IMPORT EXCEL
    # =================================================

    def load_excel(self):

        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Excel Files", "*.xlsx")
            ]
        )

        if not file_path:
            return

        try:

            df = pd.read_excel(file_path)

            self.input_text.delete(
                "1.0",
                tk.END
            )

            lines = []

            for _, row in df.iterrows():

                vals = list(row.values)

                line = " ".join(
                    map(str, vals[:-2])
                )

                line += f" {vals[-2]}"

                line += f" | {vals[-1]}"

                lines.append(line)

            self.input_text.insert(
                tk.END,
                "\n".join(lines)
            )

            messagebox.showinfo(
                "Success",
                "Excel berhasil diimport"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

    # =================================================
    # PARSE INPUT
    # =================================================

    def parse_input(self):

        n_var = int(
            self.entry_var.get()
        )

        n_goal = 5

        raw = self.input_text.get(
            "1.0",
            tk.END
        ).strip()

        lines = raw.split("\n")

        if len(lines) != 5:

            raise Exception(
                "Goal harus 5"
            )

        coef = []

        rhs = []

        objectives = []

        for line in lines:

            left, obj = line.split("|")

            obj = obj.strip().lower()

            objectives.append(obj)

            nums = list(
                map(float, left.split())
            )

            coef.append(nums[:-1])

            rhs.append(nums[-1])

        return (
            np.array(coef),
            np.array(rhs),
            objectives,
            n_var,
            n_goal
        )

    # =================================================
    # BUILD MODEL
    # =================================================

    def build_model(
        self,
        coef,
        rhs,
        objectives,
        n_var,
        n_goal
    ):

        total_vars = n_var + 2*n_goal

        A = np.zeros(
            (n_goal, total_vars)
        )

        for i in range(n_goal):

            A[i, :n_var] = coef[i]

        for i in range(n_goal):

            dm = n_var + 2*i

            dp = n_var + 2*i + 1

            A[i, dm] = 1

            A[i, dp] = -1

        c = np.zeros(total_vars)

        for i, typ in enumerate(objectives):

            dm = n_var + 2*i

            dp = n_var + 2*i + 1

            if typ == "m":

                c[dm] = 1

            elif typ == "p":

                c[dp] = 1

            elif typ == "b":

                c[dm] = 1
                c[dp] = 1

        return A, c

    # =================================================
    # SOLVE
    # =================================================

    def solve(self):

        try:

            (
                coef,
                rhs,
                objectives,
                n_var,
                n_goal
            ) = self.parse_input()

            A, c = self.build_model(
                coef,
                rhs,
                objectives,
                n_var,
                n_goal
            )

            solver = DualRevisedSimplex(
                c,
                A,
                rhs
            )

            result = solver.solve()

            self.show_result(
                result,
                coef,
                rhs,
                n_var,
                n_goal
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

    # =================================================
    # SHOW RESULT
    # =================================================

    def show_result(
        self,
        result,
        coef,
        rhs,
        n_var,
        n_goal
    ):

        self.result_text.delete(
            "1.0",
            tk.END
        )

        x = result["x"]

        goal_names = [
            "ASET",
            "LIABILITAS",
            "EKUITAS",
            "PENDAPATAN",
            "BEBAN"
        ]

        out = ""

        out += "="*120 + "\n"

        out += "GOAL PROGRAMMING RESULT\n"

        out += "="*120 + "\n\n"

        out += (
            f"Nilai Z = "
            f"{result['fun']:.6f}\n\n"
        )

        out += "VARIABLE X\n"

        out += "-"*60 + "\n"

        for i in range(n_var):

            out += (
                f"X{i+1} = "
                f"{x[i]:.6f}\n"
            )

        out += "\nDEVIASI\n"

        out += "-"*60 + "\n"

        for i in range(n_goal):

            dm = x[n_var + 2*i]

            dp = x[n_var + 2*i + 1]

            out += (
                f"{goal_names[i]}\n"
            )

            out += (
                f"d{i+1}m = {dm:.6f}\n"
            )

            out += (
                f"d{i+1}p = {dp:.6f}\n\n"
            )

        out += "\nPENCAPAIAN GOAL\n"

        out += "-"*120 + "\n"

        for i in range(n_goal):

            realisasi = np.dot(
                coef[i],
                x[:n_var]
            )

            diff = realisasi - rhs[i]

            if abs(diff) < EPS:

                status = "Tercapai"

            elif diff > 0:

                status = (
                    f"Lebih +{diff:.6f}"
                )

            else:

                status = (
                    f"Kurang {diff:.6f}"
                )

            out += (
                f"{goal_names[i]:<15}"
                f"| Realisasi = "
                f"{realisasi:>12.6f} "
                f"| Target = "
                f"{rhs[i]:>12.6f} "
                f"| {status}\n"
            )

        out += "\n"

        out += "="*120

        self.result_text.insert(
            tk.END,
            out
        )

    # =================================================
    # SAVE RESULT
    # =================================================

    def save_result(self):

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text File", "*.txt"),
                ("PDF File", "*.pdf"),
                ("Excel File", "*.xlsx")
            ]
        )

        if not file_path:
            return

        content = self.result_text.get(
            "1.0",
            tk.END
        )

        try:

            # TXT

            if file_path.endswith(".txt"):

                with open(
                    file_path,
                    "w",
                    encoding="utf-8"
                ) as f:

                    f.write(content)

            # PDF

            elif file_path.endswith(".pdf"):

                doc = SimpleDocTemplate(
                    file_path
                )

                styles = getSampleStyleSheet()

                elements = []

                elements.append(
                    Paragraph(
                        "HASIL GOAL PROGRAMMING",
                        styles['Heading1']
                    )
                )

                elements.append(
                    Spacer(1, 12)
                )

                elements.append(
                    Preformatted(
                        content,
                        styles['Code']
                    )
                )

                doc.build(elements)

            # EXCEL

            elif file_path.endswith(".xlsx"):

                lines = content.split("\n")

                df = pd.DataFrame({
                    "Hasil": lines
                })

                df.to_excel(
                    file_path,
                    index=False
                )

            messagebox.showinfo(
                "Success",
                "Hasil berhasil disimpan"
            )

        except Exception as e:

            messagebox.showerror(
                "Error Save",
                str(e)
            )


# =====================================================
# MAIN
# =====================================================

root = tk.Tk()

app = GoalProgrammingGUI(root)

root.mainloop()