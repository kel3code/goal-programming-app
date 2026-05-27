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

# =====================================================
# IMPORT LIBRARY
# =====================================================

import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText

import numpy as np
import pandas as pd

from scipy.optimize import linprog

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Preformatted
)
from reportlab.lib.styles import getSampleStyleSheet

EPS = 1e-9

# =====================================================
# THEME
# =====================================================

BG          = "#0f1117"
SURFACE     = "#1a1d27"
SURFACE2    = "#222535"
BORDER      = "#2e3248"
ACCENT      = "#4f8ef7"
ACCENT2     = "#7c5cfc"
GREEN       = "#3ecf8e"
ORANGE      = "#f97316"
YELLOW      = "#f5c518"
RED         = "#ef4444"
TEXT        = "#e8eaf6"
MUTED       = "#8891b2"
FONT_MONO   = ("Consolas", 11)
FONT_MONO_S = ("Consolas", 10)
FONT_BOLD   = ("Segoe UI", 12, "bold")
FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_LABEL  = ("Segoe UI", 11)
FONT_BTN    = ("Segoe UI", 11, "bold")
FONT_SMALL  = ("Segoe UI", 9)


def styled_button(parent, text, command, color, width=28):
    """Flat styled button with hover effect."""
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg=TEXT,
        activebackground=color,
        activeforeground=TEXT,
        font=FONT_BTN,
        width=width,
        height=2,
        relief="flat",
        bd=0,
        cursor="hand2"
    )
    def on_enter(e): btn.config(bg=_lighten(color))
    def on_leave(e): btn.config(bg=color)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def _lighten(hex_color, amount=30):
    """Slightly lighten a hex color for hover."""
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = min(255, r + amount)
    g = min(255, g + amount)
    b = min(255, b + amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def section_label(parent, text):
    """Section header with accent bar visual."""
    frame = tk.Frame(parent, bg=BG)
    tk.Frame(frame, bg=ACCENT, width=4, height=22).pack(side="left", padx=(0, 10))
    tk.Label(
        frame,
        text=text,
        font=("Segoe UI", 12, "bold"),
        bg=BG,
        fg=ACCENT
    ).pack(side="left")
    return frame


def divider(parent):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=6)


# =====================================================
# CLASS
# =====================================================

class GoalProgrammingGUI:

    # =================================================
    # INIT
    # =================================================

    def __init__(self, root):

        self.root = root

        self.root.title("ADVANCED GOAL PROGRAMMING SOLVER")
        self.root.geometry("1500x950")
        self.root.configure(bg=BG)

        # =================================================
        # CANVAS
        # =================================================

        self.canvas = tk.Canvas(root, bg=BG, highlightthickness=0)

        self.scrollbar = tk.Scrollbar(
            root,
            orient="vertical",
            command=self.canvas.yview,
            bg=SURFACE,
            troughcolor=BG
        )

        self.scrollable_frame = tk.Frame(self.canvas, bg=BG)

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

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # =================================================
        # MOUSE WHEEL
        # =================================================

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # =================================================
        # HEADER BANNER
        # =================================================

        header = tk.Frame(self.scrollable_frame, bg=SURFACE, pady=18)
        header.pack(fill="x")

        tk.Frame(header, bg=ACCENT, width=6, height=50).pack(
            side="left", padx=(24, 16)
        )

        title_col = tk.Frame(header, bg=SURFACE)
        title_col.pack(side="left")

        tk.Label(
            title_col,
            text="ADVANCED GOAL PROGRAMMING SOLVER",
            font=FONT_TITLE,
            bg=SURFACE,
            fg=TEXT
        ).pack(anchor="w")

        tk.Label(
            title_col,
            text="Optimasi Laporan Keuangan  ·  Aset · Liabilitas · Ekuitas · Pendapatan · Beban",
            font=FONT_SMALL,
            bg=SURFACE,
            fg=MUTED
        ).pack(anchor="w")

        tk.Frame(self.scrollable_frame, bg=ACCENT, height=2).pack(fill="x")

        # =================================================
        # BODY PAD
        # =================================================

        body = tk.Frame(self.scrollable_frame, bg=BG, padx=32, pady=20)
        body.pack(fill="both", expand=True)

        # =================================================
        # TOP INPUT ROW
        # =================================================

        top = tk.Frame(body, bg=SURFACE2, padx=20, pady=14)
        top.pack(fill="x", pady=(0, 16))

        tk.Label(
            top,
            text="Jumlah Variabel :",
            font=FONT_BOLD,
            bg=SURFACE2,
            fg=TEXT
        ).grid(row=0, column=0, padx=(0, 8))

        self.entry_var = tk.Entry(
            top,
            width=8,
            font=FONT_MONO,
            bg=SURFACE,
            fg=ACCENT,
            insertbackground=ACCENT,
            relief="flat",
            bd=4
        )
        self.entry_var.grid(row=0, column=1, padx=(0, 24))

        tk.Label(
            top,
            text="Goal Tetap :",
            font=FONT_BOLD,
            bg=SURFACE2,
            fg=TEXT
        ).grid(row=0, column=2, padx=(0, 8))

        tk.Label(
            top,
            text="Aset  ·  Liabilitas  ·  Ekuitas  ·  Pendapatan  ·  Beban",
            font=("Segoe UI", 11),
            bg=SURFACE2,
            fg=ACCENT
        ).grid(row=0, column=3, padx=5)

        # =================================================
        # INFO PANEL
        # =================================================

        divider(body)
        section_label(body, "FORMAT INPUT MANUAL").pack(anchor="w", pady=(4, 6))

        info_frame = tk.Frame(body, bg=SURFACE2, padx=16, pady=12)
        info_frame.pack(fill="x")

        info = (
            "FORMAT :   x1  x2  x3 ...  rhs  |  objective\n\n"
            "CONTOH :\n"
            "   45 65 90 | m\n"
            "   23 11 40 | p\n"
            "   77 88 120 | b\n"
            "   12 44 55 | m\n"
            "   88 66 33 | p\n\n"
            "KETERANGAN :\n"
            "   m  =  minimize deviasi minus\n"
            "   p  =  minimize deviasi plus\n"
            "   b  =  minimize keduanya\n\n"
            "GOAL WAJIB 5 :   1.Aset   2.Liabilitas   3.Ekuitas   4.Pendapatan   5.Beban"
        )

        tk.Label(
            info_frame,
            text=info,
            justify="left",
            font=FONT_MONO,
            bg=SURFACE2,
            fg=MUTED
        ).pack(anchor="w")

        # =================================================
        # INPUT MODEL
        # =================================================

        divider(body)
        section_label(body, "INPUT MODEL").pack(anchor="w", pady=(4, 6))

        self.input_text = ScrolledText(
            body,
            width=150,
            height=20,
            font=FONT_MONO,
            bg=SURFACE2,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            bd=0,
            selectbackground=ACCENT2,
            selectforeground=TEXT,
            padx=12,
            pady=10
        )
        self.input_text.pack(pady=(0, 12), fill="x")

        # =================================================
        # BUTTONS ROW
        # =================================================

        divider(body)
        btn_frame = tk.Frame(body, bg=BG)
        btn_frame.pack(pady=10)

        styled_button(
            btn_frame,
            "📂  IMPORT EXCEL",
            self.load_excel,
            "#1a5c36",
            width=24
        ).pack(side="left", padx=8)

        styled_button(
            btn_frame,
            "▶   SOLVE GOAL PROGRAMMING",
            self.solve,
            ACCENT,
            width=34
        ).pack(side="left", padx=8)

        styled_button(
            btn_frame,
            "💾  SAVE RESULT",
            self.save_result,
            "#b45309",
            width=24
        ).pack(side="left", padx=8)

        # =================================================
        # RESULT
        # =================================================

        divider(body)
        section_label(body, "HASIL").pack(anchor="w", pady=(4, 6))

        self.result_text = ScrolledText(
            body,
            width=170,
            height=35,
            font=FONT_MONO_S,
            bg=SURFACE2,
            fg=GREEN,
            insertbackground=ACCENT,
            relief="flat",
            bd=0,
            selectbackground=ACCENT2,
            selectforeground=TEXT,
            padx=12,
            pady=10
        )
        self.result_text.pack(pady=(0, 24), fill="x")

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

    # =================================================
    # PARSE INPUT
    # =================================================

    def parse_input(self):

        n_var = int(self.entry_var.get())

        n_goal = 5

        raw = self.input_text.get("1.0", tk.END).strip()

        if not raw:
            raise ValueError("Input model kosong")

        lines = raw.split("\n")

        if len(lines) != n_goal:
            raise ValueError("Jumlah goal harus 5")

        coef       = []
        rhs        = []
        objectives = []

        for line in lines:

            if "|" not in line:
                raise ValueError("Gunakan format: data | objective")

            left, obj = line.split("|")

            obj = obj.strip().lower()

            objectives.append(obj)

            nums = list(map(float, left.split()))

            if len(nums) != n_var + 1:
                raise ValueError(
                    f"Baris harus berisi {n_var} variabel + 1 rhs"
                )

            coef.append(nums[:-1])
            rhs.append(nums[-1])

        coef = np.array(coef)
        rhs  = np.array(rhs)

        return coef, rhs, objectives, n_var, n_goal

    # =================================================
    # BUILD MODEL
    # =================================================

    def build_model(self, coef, rhs, objectives, n_var, n_goal):

        total_vars = n_var + 2 * n_goal

        A_eq = np.zeros((n_goal, total_vars))

        for i in range(n_goal):
            A_eq[i, :n_var] = coef[i]

        # deviasi
        for i in range(n_goal):
            d_minus = n_var + 2*i
            d_plus  = n_var + 2*i + 1
            A_eq[i, d_minus] =  1
            A_eq[i, d_plus]  = -1

        # objective
        c = np.zeros(total_vars)

        for i, typ in enumerate(objectives):
            d_minus = n_var + 2*i
            d_plus  = n_var + 2*i + 1
            if typ == "m":
                c[d_minus] = 1
            elif typ == "p":
                c[d_plus] = 1
            elif typ == "b":
                c[d_minus] = 1
                c[d_plus]  = 1

        return A_eq, c

    # =================================================
    # SOLVE
    # =================================================

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
    # SHOW RESULT
    # =================================================

    def show_result(self, result, coef, rhs, n_var, n_goal):

        self.result_text.delete("1.0", tk.END)

        x = result.x

        goal_names = [
            "ASET",
            "LIABILITAS",
            "EKUITAS",
            "PENDAPATAN",
            "BEBAN"
        ]

        out = ""

        out += "=" * 120 + "\n"
        out += "HASIL GOAL PROGRAMMING\n"
        out += "=" * 120 + "\n\n"

        out += f"Nilai Z = {result.fun:.6f}\n\n"

        # X
        out += "VARIABLE X\n"
        out += "-" * 60 + "\n"

        for i in range(n_var):
            val = x[i]
            if abs(val) < EPS:
                val = 0
            out += f"X{i+1:<3} = {val:.6f}\n"

        # deviasi
        out += "\nDEVIASI\n"
        out += "-" * 60 + "\n"

        for i in range(n_goal):
            dm = x[n_var + 2*i]
            dp = x[n_var + 2*i + 1]
            out += f"{goal_names[i]}:\n"
            out += f"   d{i+1}m = {dm:.6f}\n"
            out += f"   d{i+1}p = {dp:.6f}\n\n"

        # pencapaian
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

        try:

            content = self.result_text.get("1.0", tk.END)

            # TXT
            if file_path.endswith(".txt"):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

            # PDF
            elif file_path.endswith(".pdf"):
                doc      = SimpleDocTemplate(file_path)
                styles   = getSampleStyleSheet()
                elements = []
                elements.append(
                    Paragraph("HASIL GOAL PROGRAMMING", styles['Heading1'])
                )
                elements.append(Spacer(1, 12))
                elements.append(
                    Preformatted(content, styles['Code'])
                )
                doc.build(elements)

            # EXCEL
            elif file_path.endswith(".xlsx"):
                lines = content.split("\n")
                df = pd.DataFrame({"Hasil": lines})
                df.to_excel(file_path, index=False)

            messagebox.showinfo("Success", "Hasil berhasil disimpan")

        except Exception as e:

            messagebox.showerror("Error Save", str(e))


# =====================================================
# MAIN
# =====================================================

root = tk.Tk()

app = GoalProgrammingGUI(root)

root.mainloop()