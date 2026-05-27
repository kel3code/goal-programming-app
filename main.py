import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import numpy as np

# =========================================================
# EPSILON
# =========================================================

EPSILON = 1e-9

# =========================================================
# SIMPLEX GOAL PROGRAMMING
# =========================================================

class GoalProgrammingSolver:

    def __init__(self):

        self.num_x = 0
        self.num_goal = 0

        self.var_names = []

        self.c = None
        self.A = None
        self.b = None

        self.basis = []
        self.non_basis = []

        self.solution = None

        self.iterations = []

    # =====================================================
    # BUILD MODEL
    # =====================================================

    def build_model(self, num_x, num_goal, goal_data):

        self.num_x = num_x
        self.num_goal = num_goal

        self.var_names = []

        # -------------------------------------------------
        # x variables
        # -------------------------------------------------

        for i in range(num_x):

            self.var_names.append(f"x{i+1}")

        # -------------------------------------------------
        # deviasi
        # -------------------------------------------------

        for i in range(num_goal):

            self.var_names.append(f"d{i+1}p")
            self.var_names.append(f"d{i+1}m")

        total_vars = num_x + (2 * num_goal)

        # -------------------------------------------------
        # fungsi tujuan
        # -------------------------------------------------

        self.c = np.zeros(total_vars)

        rows = []
        rhs_values = []

        for i, goal in enumerate(goal_data):

            coeffs = goal["coeffs"]
            rhs = goal["rhs"]
            minimize = goal["minimize"]

            row = []

            # x
            row.extend(coeffs)

            # deviasi
            for j in range(num_goal):

                if i == j:

                    # d+
                    row.append(-1)

                    # d-
                    row.append(1)

                    # fungsi tujuan
                    if minimize == "d+":

                        self.c[num_x + (2 * j)] = 1

                    elif minimize == "d-":

                        self.c[num_x + (2 * j) + 1] = 1

                    elif minimize == "both":

                        self.c[num_x + (2 * j)] = 1
                        self.c[num_x + (2 * j) + 1] = 1

                else:

                    row.append(0)
                    row.append(0)

            rows.append(row)
            rhs_values.append(rhs)

        self.A = np.array(rows, dtype=float)

        self.b = np.array(rhs_values, dtype=float)

        # -------------------------------------------------
        # basis awal = d-
        # -------------------------------------------------

        self.basis = []

        for i in range(num_goal):

            self.basis.append(
                num_x + (2 * i) + 1
            )

        self.non_basis = [

            j for j in range(total_vars)

            if j not in self.basis
        ]

    # =====================================================
    # SOLVE
    # =====================================================

    def solve(self):

        iteration = 1

        m, n = self.A.shape

        self.iterations = []

        while True:

            B = self.A[:, self.basis]

            try:

                B_inv = np.linalg.inv(B)

            except:

                raise Exception(
                    "Matrix singular / tidak memiliki inverse"
                )

            xb = B_inv @ self.b

            cb = self.c[self.basis]

            zj = cb @ B_inv @ self.A

            reduced_costs = self.c - zj

            # -------------------------------------------------
            # simpan iterasi
            # -------------------------------------------------

            iter_data = {
                "iteration": iteration,
                "basis": [],
                "values": [],
                "reduced": {}
            }

            for i, basis_var in enumerate(self.basis):

                iter_data["basis"].append(
                    self.var_names[basis_var]
                )

                iter_data["values"].append(
                    xb[i]
                )

            for j in self.non_basis:

                iter_data["reduced"][
                    self.var_names[j]
                ] = reduced_costs[j]

            self.iterations.append(iter_data)

            # -------------------------------------------------
            # entering variable
            # minimisasi => paling negatif
            # -------------------------------------------------

            entering = None

            min_value = 0

            for j in self.non_basis:

                if reduced_costs[j] < min_value:

                    min_value = reduced_costs[j]

                    entering = j

            # -------------------------------------------------
            # optimal
            # -------------------------------------------------

            if entering is None:

                break

            # -------------------------------------------------
            # direction
            # -------------------------------------------------

            aj = self.A[:, entering]

            direction = B_inv @ aj

            # -------------------------------------------------
            # ratio test
            # -------------------------------------------------

            ratios = []

            for i in range(m):

                if direction[i] > EPSILON:

                    ratios.append(
                        xb[i] / direction[i]
                    )

                else:

                    ratios.append(np.inf)

            leaving_row = np.argmin(ratios)

            # -------------------------------------------------
            # update basis
            # -------------------------------------------------

            self.basis[leaving_row] = entering

            self.non_basis = [

                j for j in range(n)

                if j not in self.basis
            ]

            iteration += 1

            # pengaman looping
            if iteration > 100:

                raise Exception(
                    "Iterasi terlalu banyak"
                )

        # -------------------------------------------------
        # solusi akhir
        # -------------------------------------------------

        self.solution = np.zeros(n)

        for i, var in enumerate(self.basis):

            value = xb[i]

            if abs(value) < EPSILON:

                value = 0

            # non negatif
            if value < 0:

                value = 0

            self.solution[var] = value

        z = np.dot(self.c, self.solution)

        return self.solution, z

# =========================================================
# GUI
# =========================================================

class GPApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Goal Programming - Revised Simplex"
        )

        self.root.geometry("1400x900")

        self.root.configure(bg="#f3f4f6")

        self.goal_frames = []

        self.create_widgets()

    # =====================================================
    # CREATE WIDGETS
    # =====================================================

    def create_widgets(self):

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        title = tk.Label(

            self.root,

            text="GOAL PROGRAMMING - REVISED SIMPLEX",

            font=("Arial", 22, "bold"),

            bg="#f3f4f6",

            fg="#111827"
        )

        title.pack(pady=15)

        # -------------------------------------------------
        # TOP FRAME
        # -------------------------------------------------

        top_frame = tk.Frame(

            self.root,

            bg="#f3f4f6"
        )

        top_frame.pack(fill="x", padx=20)

        # jumlah variabel

        tk.Label(

            top_frame,

            text="Jumlah Variabel",

            font=("Arial", 12),

            bg="#f3f4f6"

        ).grid(row=0, column=0, padx=5)

        self.var_entry = tk.Entry(

            top_frame,

            width=10,

            font=("Arial", 12)
        )

        self.var_entry.grid(row=0, column=1)

        # jumlah goal

        tk.Label(

            top_frame,

            text="Jumlah Goal",

            font=("Arial", 12),

            bg="#f3f4f6"

        ).grid(row=0, column=2, padx=5)

        self.goal_entry = tk.Entry(

            top_frame,

            width=10,

            font=("Arial", 12)
        )

        self.goal_entry.grid(row=0, column=3)

        # generate button

        generate_btn = tk.Button(

            top_frame,

            text="Generate Input",

            font=("Arial", 11, "bold"),

            bg="#2563eb",

            fg="white",

            command=self.generate_inputs
        )

        generate_btn.grid(row=0, column=4, padx=10)

        # -------------------------------------------------
        # SCROLL AREA
        # -------------------------------------------------

        self.canvas = tk.Canvas(

            self.root,

            bg="#f3f4f6"
        )

        self.scrollbar = ttk.Scrollbar(

            self.root,

            orient="vertical",

            command=self.canvas.yview
        )

        self.scrollable_frame = tk.Frame(

            self.canvas,

            bg="#f3f4f6"
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

            expand=True,

            padx=20,

            pady=10
        )

        self.scrollbar.pack(

            side="right",

            fill="y"
        )

        # -------------------------------------------------
        # BUTTON FRAME
        # -------------------------------------------------

        button_frame = tk.Frame(

            self.root,

            bg="#f3f4f6"
        )

        button_frame.pack(fill="x", pady=10)

        solve_btn = tk.Button(

            button_frame,

            text="SOLVE",

            font=("Arial", 14, "bold"),

            bg="#16a34a",

            fg="white",

            width=15,

            command=self.solve_model
        )

        solve_btn.pack(side="left", padx=20)

        # -------------------------------------------------
        # OUTPUT TEXT
        # -------------------------------------------------

        self.output_text = tk.Text(

            self.root,

            height=20,

            font=("Consolas", 11),

            bg="#111827",

            fg="#22c55e"
        )

        self.output_text.pack(

            fill="both",

            expand=True,

            padx=20,

            pady=15
        )

    # =====================================================
    # GENERATE INPUT
    # =====================================================

    def generate_inputs(self):

        for widget in self.scrollable_frame.winfo_children():

            widget.destroy()

        self.goal_frames = []

        try:

            num_x = int(self.var_entry.get())

            num_goal = int(self.goal_entry.get())

        except:

            messagebox.showerror(
                "Error",
                "Input jumlah salah"
            )

            return

        for i in range(num_goal):

            frame = tk.LabelFrame(

                self.scrollable_frame,

                text=f"Goal {i+1}",

                font=("Arial", 12, "bold"),

                padx=10,

                pady=10,

                bg="white"
            )

            frame.pack(

                fill="x",

                padx=10,

                pady=10
            )

            # koefisien

            tk.Label(

                frame,

                text=f"Koefisien x1-x{num_x}",

                bg="white"

            ).grid(row=0, column=0)

            coeff_entry = tk.Entry(

                frame,

                width=60
            )

            coeff_entry.grid(

                row=0,

                column=1,

                padx=10
            )

            # rhs

            tk.Label(

                frame,

                text="RHS",

                bg="white"

            ).grid(row=1, column=0)

            rhs_entry = tk.Entry(

                frame,

                width=20
            )

            rhs_entry.grid(

                row=1,

                column=1,

                sticky="w",

                padx=10,

                pady=5
            )

            # minimisasi

            tk.Label(

                frame,

                text="Minimasi",

                bg="white"

            ).grid(row=2, column=0)

            combo = ttk.Combobox(

                frame,

                values=[
                    "d+",
                    "d-",
                    "both"
                ],

                width=20
            )

            combo.current(0)

            combo.grid(

                row=2,

                column=1,

                sticky="w",

                padx=10,

                pady=5
            )

            self.goal_frames.append({

                "coeff": coeff_entry,

                "rhs": rhs_entry,

                "combo": combo
            })

    # =====================================================
    # SOLVE MODEL
    # =====================================================

    def solve_model(self):

        try:

            num_x = int(self.var_entry.get())

            num_goal = int(self.goal_entry.get())

            goal_data = []

            for frame in self.goal_frames:

                coeffs = list(

                    map(

                        float,

                        frame["coeff"].get().split()
                    )
                )

                if len(coeffs) != num_x:

                    raise Exception(
                        "Jumlah koefisien salah"
                    )

                rhs = float(
                    frame["rhs"].get()
                )

                minimize = frame["combo"].get()

                goal_data.append({

                    "coeffs": coeffs,

                    "rhs": rhs,

                    "minimize": minimize
                })

            solver = GoalProgrammingSolver()

            solver.build_model(

                num_x,

                num_goal,

                goal_data
            )

            solution, z = solver.solve()

            self.output_text.delete(

                1.0,

                tk.END
            )

            # -------------------------------------------------
            # iterasi
            # -------------------------------------------------

            self.output_text.insert(

                tk.END,

                "=" * 70 + "\n"
            )

            self.output_text.insert(

                tk.END,

                "ITERASI SIMPLEX\n"
            )

            self.output_text.insert(

                tk.END,

                "=" * 70 + "\n\n"
            )

            for data in solver.iterations:

                self.output_text.insert(

                    tk.END,

                    f"ITERASI {data['iteration']}\n"
                )

                self.output_text.insert(

                    tk.END,

                    "-" * 50 + "\n"
                )

                for b, val in zip(

                    data["basis"],

                    data["values"]
                ):

                    self.output_text.insert(

                        tk.END,

                        f"{b} = {val:.10f}\n"
                    )

                self.output_text.insert(

                    tk.END,

                    "\nCj - Zj\n"
                )

                for key, val in data[
                    "reduced"
                ].items():

                    self.output_text.insert(

                        tk.END,

                        f"{key} = {val:.10f}\n"
                    )

                self.output_text.insert(

                    tk.END,

                    "\n"
                )

            # -------------------------------------------------
            # solusi akhir
            # -------------------------------------------------

            self.output_text.insert(

                tk.END,

                "=" * 70 + "\n"
            )

            self.output_text.insert(

                tk.END,

                "SOLUSI AKHIR\n"
            )

            self.output_text.insert(

                tk.END,

                "=" * 70 + "\n"
            )

            for i, var in enumerate(
                solver.var_names
            ):

                self.output_text.insert(

                    tk.END,

                    f"{var} = {solution[i]:.10f}\n"
                )

            self.output_text.insert(

                tk.END,

                f"\nNilai Z = {z:.10f}\n"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

# =========================================================
# MAIN
# =========================================================

root = tk.Tk()

app = GPApp(root)

root.mainloop()