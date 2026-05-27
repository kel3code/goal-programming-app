"""
ADVANCED GOAL PROGRAMMING GUI
======================================================
✔ FULL SCROLLABLE WINDOW
✔ Mouse wheel support
✔ Fast input
✔ Objective langsung per baris
✔ Input besar tetap nyaman
✔ Flexible Goal Programming

FORMAT INPUT:

x1 x2 x3 ... rhs | objective

Contoh:

45 65 90 | m
23 11 40 | p
77 88 120 | t

Keterangan:
m = minimize deviasi minus
p = minimize deviasi plus
t = tidak masuk objective
"""
#import library#
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

import numpy as np  #untuk operasi matriks
from scipy.optimize import linprog #solver optimasi linier programming

EPS = 1e-9  #toleransi nilai error

class GoalProgrammingGUI:

    def __init__(self, root): #tampilan gui

        self.root = root  #window utama

        self.root.title(
            "Advanced Goal Programming Solver"
        )

        self.root.geometry("1400x900")

        # =================================================
        # MAIN CANVAS
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

        # =================================================
        # MOUSE WHEEL Menghubungkan scroll maose ke canvas
        # =================================================
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
        # TOP INPUT
        # =================================================
        top = tk.Frame(self.scrollable_frame)

        top.pack(pady=10)

        tk.Label(
            top,
            text="Jumlah Variabel:",
            font=("Arial", 12, "bold")
        ).grid(row=0, column=0, padx=5)

        self.entry_var = tk.Entry(  #input jumlah variabel
            top,
            width=10,
            font=("Arial", 12)
        )

        self.entry_var.grid(row=0, column=1) 

        tk.Label(
            top,
            text="Jumlah Goal:",
            font=("Arial", 12, "bold")
        ).grid(row=0, column=2, padx=5)

        self.entry_goal = tk.Entry( #input jumlah goal
            top,
            width=10,
            font=("Arial", 12)
        )

        self.entry_goal.grid(row=0, column=3)

        # =================================================
        # INFO PETUNJUK PENGISIAN MODEL
        # =================================================
        info = """
FORMAT INPUT

x1 x2 x3 ... rhs | objective

Contoh:

45 65 90 | m
23 11 40 | p
77 88 120 | t

m = minimize deviasi minus
p = minimize deviasi plus
t = tidak masuk objective

Kolom terakhir sebelum | dianggap RHS
"""

        tk.Label(
            self.scrollable_frame,
            text=info,
            justify="left",
            font=("Consolas", 11)
        ).pack(pady=10)

        # =================================================
        # INPUT MODEL
        # =================================================
        tk.Label(
            self.scrollable_frame,
            text="INPUT MODEL",
            font=("Arial", 14, "bold")
        ).pack()

        self.input_text = ScrolledText( #Tempat untuk memasukkan model
            self.scrollable_frame,
            width=140,
            height=20,
            font=("Consolas", 11)
        )

        self.input_text.pack(pady=10)

        # =================================================
        # BUTTON
        # =================================================
        tk.Button(
            self.scrollable_frame,
            text="SOLVE GOAL PROGRAMMING",
            command=self.solve,
            bg="#2196F3",
            fg="white",
            font=("Arial", 14, "bold"),
            width=35,
            height=2
        ).pack(pady=20)

        # =================================================
        # RESULT TAMPILAN HASIL
        # =================================================
        tk.Label(
            self.scrollable_frame,
            text="HASIL",
            font=("Arial", 14, "bold")
        ).pack()

        self.result_text = ScrolledText(
            self.scrollable_frame,
            width=160,
            height=30,
            font=("Consolas", 10)
        )

        self.result_text.pack(
            pady=10,
            padx=10
        )

    # =====================================================
    # MOUSE WHEEL
    # =====================================================

    def _on_mousewheel(self, event):

        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    # =====================================================
    # PARSE INPUT Mengubah menjadi matriks matematika
    # =====================================================

    def parse_input(self):

        n_var = int(self.entry_var.get()) #ambil jumlah variabel
        n_goal = int(self.entry_goal.get()) #ambil jumlah goal

        raw = self.input_text.get(
            "1.0",
            tk.END
        ).strip()

        if not raw:

            raise ValueError(
                "Input model kosong"
            )

        lines = raw.split("\n") #split per baris

        if len(lines) != n_goal: #validasi jumlah goal

            raise ValueError(
                f"Jumlah goal harus {n_goal}"
            )

        coef = []
        rhs = []
        objectives = []

        for line in lines:

            # ---------------------------------------------
            # SPLIT objective
            # ---------------------------------------------
            if "|" not in line:

                raise ValueError(
                    "Gunakan format: data | objective"
                )

            left, obj = line.split("|") #untuk memisahkan objektif

            obj = obj.strip().lower()

            objectives.append(obj)

            nums = list(
                map(float, left.split()) #mengubah menjadi angka
            )

            # x + rhs
            if len(nums) != n_var + 1:

                raise ValueError(
                    f"Baris harus berisi "
                    f"{n_var} variabel + 1 rhs"
                )

            coef.append(nums[:-1]) #memisahkan koefisien dengan target

            rhs.append(nums[-1])

        coef = np.array(coef)
        rhs = np.array(rhs)

        return (
            coef,
            rhs,
            objectives,
            n_var,
            n_goal
        )

    # =====================================================
    # BUILD MODEL
    # =====================================================

    def build_model(
        self,
        coef,
        rhs,
        objectives,
        n_var,
        n_goal
    ):

        total_vars = n_var + 2 * n_goal #total variabel

        A_eq = np.zeros(
            (n_goal, total_vars) #membuat matriks nol
        )

        for i in range(n_goal):

            A_eq[i, :n_var] = coef[i] #isi koefisien variabel keputusan

        # deviasi
        for i in range(n_goal):

            d_minus = n_var + 2*i
            d_plus = n_var + 2*i + 1

            A_eq[i, d_minus] = 1
            A_eq[i, d_plus] = -1

        # membuat fungsi objective
        c = np.zeros(total_vars)

        for i, typ in enumerate(objectives):

            d_minus = n_var + 2*i
            d_plus = n_var + 2*i + 1

            if typ == "m": #ketika minimum minus

                c[d_minus] = 1

            elif typ == "p":#ketika plus

                c[d_plus] = 1

        return A_eq, c

    # =====================================================
    # SOLVE
    # =====================================================

    def solve(self):

        try:

            (
                coef,
                rhs,
                objectives,
                n_var,
                n_goal
            ) = self.parse_input()

            A_eq, c = self.build_model(
                coef,
                rhs,
                objectives,
                n_var,
                n_goal
            )

            bounds = [
                (0, None)
            ] * len(c)

            result = linprog( #jalankan solver
                c=c,
                A_eq=A_eq,
                b_eq=rhs,
                bounds=bounds,
                method='highs'
            )

            if result.status != 0:

                messagebox.showerror(
                    "Error",
                    result.message
                )

                return

            self.show_result( #menampilkan hasil 
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

    # =====================================================
    # SHOW RESULT
    # =====================================================

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

        x = result.x # semua variabel optimal

        out = ""

        out += "=" * 100 + "\n"
        out += "HASIL GOAL PROGRAMMING\n"
        out += "=" * 100 + "\n\n"

        out += (
            f"Nilai Z = "
            f"{result.fun:.6f}\n\n"
        )

        # variable x
        out += "VARIABLE X\n"
        out += "-" * 50 + "\n"

        for i in range(n_var): #tampilan variabel keputusan

            val = x[i]

            if abs(val) < EPS:
                val = 0

            out += (
                f"X{i+1:<3}"
                f" = {val:.6f}\n"
            )

        # deviasi
        out += "\nDEVIASI\n"
        out += "-" * 50 + "\n"

        for i in range(n_goal):

            dm = x[n_var + 2*i]  # tampilan deviasi 
            dp = x[n_var + 2*i + 1]

            out += (
                f"d{i+1}m = {dm:.6f}\n"
            )

            out += (
                f"d{i+1}p = {dp:.6f}\n"
            )

        # pencapaian
        out += "\nPENCAPAIAN GOAL\n"
        out += "-" * 100 + "\n"

        for i in range(n_goal):

            realisasi = np.dot( #menghitung realisasi goal
                coef[i],
                x[:n_var]
            )

            diff = realisasi - rhs[i] # selisih target

            if abs(diff) < 1e-6:

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
                f"Goal {i+1:<3} | "
                f"Realisasi = "
                f"{realisasi:>12.6f} | "
                f"Target = "
                f"{rhs[i]:>12.6f} | "
                f"{status}\n"
            )

        out += "\n" + "=" * 100

        self.result_text.insert(
            tk.END,
            out
        )

# =========================================================
# MAIN
# =========================================================

root = tk.Tk()

app = GoalProgrammingGUI(root)

root.mainloop()

