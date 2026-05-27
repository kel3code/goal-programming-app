"""
ADVANCED GOAL PROGRAMMING GUI
======================================================
✔ FULL SCROLLABLE WINDOW
✔ Mouse wheel support
✔ IMPORT EXCEL
✔ SAVE TXT / PDF / EXCEL
✔ Fixed 5 Goals
✔ Goal Objective:
      m = minimize deviasi minus
      p = minimize deviasi plus
      b = minimize keduanya
======================================================
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet

EPS = 1e-9


class GoalProgrammingGUI:
    # =================================================
    # INIT & WINDOW SETUP
    # =================================================
    def __init__(self, root):
        self.root = root
        self.root.title("ADVANCED GOAL PROGRAMMING SOLVER")
        self.root.geometry("1500x950")

        # Setup Canvas dan Scrollbar
        self.canvas = tk.Canvas(root)
        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Mouse Wheel Support
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Komponen UI
        self._build_ui()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # =================================================
    # INTERFACE BUILDER
    # =================================================
    def _build_ui(self):
        # Title
        tk.Label(
            self.scrollable_frame,
            text="ADVANCED GOAL PROGRAMMING SOLVER",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        # Top Input Frame (Jumlah Variabel & Keterangan Goal)
        top_frame = tk.Frame(self.scrollable_frame)
        top_frame.pack(pady=10)

        tk.Label(
            top_frame,
            text="Jumlah Variabel:",
            font=("Arial", 12, "bold")
        ).grid(row=0, column=0, padx=5)

        self.entry_var = tk.Entry(top_frame, width=10, font=("Arial", 12))
        self.entry_var.grid(row=0, column=1)

        tk.Label(
            top_frame,
            text="Goal Tetap:",
            font=("Arial", 12, "bold")
        ).grid(row=0, column=2, padx=5)

        tk.Label(
            top_frame,
            text="Aset, Liabilitas, Ekuitas, Pendapatan, Beban",
            font=("Arial", 11),
            fg="blue"
        ).grid(row=0, column=3, padx=5)

        # Info Panduan Format
        info_text = """
FORMAT INPUT MANUAL

x1 x2 x3 ... rhs | objective

Contoh:
45 65 90 | m
23 11 40 | p
77 88 120 | b
12 44 55 | m
88 66 33 | p

Keterangan:
m = minimize deviasi minus
p = minimize deviasi plus
b = minimize keduanya

Jumlah goal wajib 5:
1. Aset  2. Liabilitas  3. Ekuitas  4. Pendapatan  5. Beban
"""
        tk.Label(
            self.scrollable_frame,
            text=info_text,
            justify="left",
            font=("Consolas", 11)
        ).pack(pady=10)

        # Area Input Model
        tk.Label(
            self.scrollable_frame,
            text="INPUT MODEL",
            font=("Arial", 14, "bold")
        ).pack()

        self.input_text = ScrolledText(
            self.scrollable_frame,
            width=150,
            height=20,
            font=("Consolas", 11)
        )
        self.input_text.pack(pady=10)

        # Tombol Aksi
        tk.Button(
            self.scrollable_frame,
            text="IMPORT EXCEL",
            command=self.load_excel,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            width=30,
            height=2
        ).pack(pady=10)

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
        ).pack(pady=10)

        # Area Hasil Output
        tk.Label(
            self.scrollable_frame,
            text="HASIL",
            font=("Arial", 14, "bold")
        ).pack()

        self.result_text = ScrolledText(
            self.scrollable_frame,
            width=170,
            height=35,
            font=("Consolas", 10)
        )
        self.result_text.pack(pady=10, padx=10)

    # =================================================
    # CORE LOGIC & PROCESSING
    # =================================================
    def load_excel(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if not file_path:
            return

        try:
            df = pd.read_excel(file_path)
            self.input_text.delete("1.0", tk.END)
            lines = []

            for _, row in df.iterrows():
                vals = list(row.values)
                line = " ".join(map(str, vals[:-2]))
                line += f" {vals[-2]}"
                line += f" | {vals[-1]}"
                lines.append(line)

            self.input_text.insert(tk.END, "\n".join(lines))
            messagebox.showinfo("Success", "Excel berhasil diimport")

        except Exception as e:
            messagebox.showerror("Error Excel", str(e))

    def parse_input(self):
        n_var = int(self.entry_var.get())
        n_goal = 5

        raw = self.input_text.get("1.0", tk.END).strip()
        if not raw:
            raise ValueError("Input model kosong")

        lines = raw.split("\n")
        if len(lines) != n_goal:
            raise ValueError("Jumlah goal harus 5")

        coef = []
        rhs = []
        objectives = []

        for line in lines:
            if "|" not in line:
                raise ValueError("Gunakan format: data | objective")

            left, obj = line.split("|")
            obj = obj.strip().lower()
            objectives.append(obj)

            nums = list(map(float, left.split()))
            if len(nums) != n_var + 1:
                raise ValueError(f"Baris harus berisi {n_var} variabel + 1 rhs")

            coef.append(nums[:-1])
            rhs.append(nums[-1])

        return np.array(coef), np.array(rhs), objectives, n_var, n_goal

    def build_model(self, coef, rhs, objectives, n_var, n_goal):
        total_vars = n_var + 2 * n_goal
        A_eq = np.zeros((n_goal, total_vars))

        for i in range(n_goal):
            A_eq[i, :n_var] = coef[i]

        # Matriks Deviasi
        for i in range(n_goal):
            d_minus = n_var + 2 * i
            d_plus = n_var + 2 * i + 1
            A_eq[i, d_minus] = 1
            A_eq[i, d_plus] = -1

        # Vektor Koefisien Fungsi Objektif (c)
        c = np.zeros(total_vars)
        for i, typ in enumerate(objectives):
            d_minus = n_var + 2 * i
            d_plus = n_var + 2 * i + 1

            if typ == "m":      # minimize minus
                c[d_minus] = 1
            elif typ == "p":    # minimize plus
                c[d_plus] = 1
            elif typ == "b":    # minimize keduanya
                c[d_minus] = 1
                c[d_plus] = 1

        return A_eq, c

    def solve(self):
        try:
            coef, rhs, objectives, n_var, n_goal = self.parse_input()
            A_eq, c = self.build_model(coef, rhs, objectives, n_var, n_goal)
            bounds = [(0, None)] * len(c)

            result = linprog(
                c=c,
                A_eq=A_eq,
                b_eq=rhs,
                bounds=bounds,
                method='highs'
            )

            if result.status != 0:
                messagebox.showerror("Error", result.message)
                return

            self.show_result(result, coef, rhs, n_var, n_goal)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =================================================
    # OUTPUT & EXPORT MANAGEMENT
    # =================================================
    def show_result(self, result, coef, rhs, n_var, n_goal):
        self.result_text.delete("1.0", tk.END)
        x = result.x
        goal_names = ["ASET", "LIABILITAS", "EKUITAS", "PENDAPATAN", "BEBAN"]

        out = "=" * 120 + "\n"
        out += "HASIL GOAL PROGRAMMING\n"
        out += "=" * 120 + "\n\n"
        out += f"Nilai Z = {result.fun:.6f}\n\n"

        # Tampilkan Nilai X
        out += "VARIABLE X\n"
        out += "-" * 60 + "\n"
        for i in range(n_var):
            val = x[i]
            if abs(val) < EPS:
                val = 0
            out += f"X{i+1:<3} = {val:.6f}\n"

        # Tampilkan Nilai Deviasi
        out += "\nDEVIASI\n"
        out += "-" * 60 + "\n"
        for i in range(n_goal):
            dm = x[n_var + 2 * i]
            dp = x[n_var + 2 * i + 1]
            out += f"{goal_names[i]}:\n"
            out += f"   d{i+1}m = {dm:.6f}\n"
            out += f"   d{i+1}p = {dp:.6f}\n\n"

        # Tampilkan Pencapaian Goal
        out += "\nPENCAPAIAN GOAL\n"
        out += "-" * 120 + "\n"
        for i in range(n_goal):
            realisasi = np.dot(coef[i], x[:n_var])
            diff = realisasi - rhs[i]

            if abs(diff) < 1e-6:
                status = "Tercapai"
            elif diff > 0:
                status = f"Lebih +{diff:.6f}"
            else:
                status = f"Kurang {diff:.6f}"

            out += (
                f"{goal_names[i]:<15} | "
                f"Realisasi = {realisasi:>15.6f} | "
                f"Target = {rhs[i]:>15.6f} | "
                f"{status}\n"
            )

        out += "\n" + "=" * 120
        self.result_text.insert(tk.END, out)

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

        try:
            content = self.result_text.get("1.0", tk.END)

            # Ekspor ke TXT
            if file_path.endswith(".txt"):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

            # Ekspor ke PDF
            elif file_path.endswith(".pdf"):
                doc = SimpleDocTemplate(file_path)
                styles = getSampleStyleSheet()
                elements = [
                    Paragraph("HASIL GOAL PROGRAMMING", styles['Heading1']),
                    Spacer(1, 12),
                    Preformatted(content, styles['Code'])
                ]
                doc.build(elements)

            # Ekspor ke Excel
            elif file_path.endswith(".xlsx"):
                lines = content.split("\n")
                df = pd.DataFrame({"Hasil": lines})
                df.to_excel(file_path, index=False)

            messagebox.showinfo("Success", "Hasil berhasil disimpan")

        except Exception as e:
            messagebox.showerror("Error Save", str(e))


# =====================================================
# MAIN EXECUTION
# =====================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = GoalProgrammingGUI(root)
    root.mainloop()