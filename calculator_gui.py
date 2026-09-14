import tkinter as tk
from tkinter import ttk, messagebox
import math
import statistics
from pathlib import Path

HISTORY_FILE = "calculator_history.txt"
RATES_FILE = "rates.txt"


class CalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Apoorv's Calculator")
        self.root.geometry("1050x700")
        self.root.minsize(900, 620)

        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
        self.style.configure("Card.TLabelframe", padding=14)
        self.style.configure("Card.TLabelframe.Label", font=("Segoe UI", 12, "bold"))
        self.style.configure("TButton", font=("Segoe UI", 10), padding=8)
        self.style.configure("TLabel", font=("Segoe UI", 10))
        self.style.configure("TCombobox", padding=5)

        header = ttk.Frame(root, padding=(20, 16, 20, 8))
        header.pack(fill="x")
        ttk.Label(header, text="APOORV'S CALCULATOR", style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="View History", command=self.view_history).pack(side="right", padx=5)
        ttk.Button(header, text="Clear History", command=self.clear_history).pack(side="right")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        self.make_arithmetic_tab()
        self.make_statistics_tab()
        self.make_converter_tab()
        self.make_finance_tab()
        self.make_geometry_tab()
        self.make_extra_tab()

        self.status = tk.StringVar(value="Ready")
        ttk.Label(root, textvariable=self.status, relief="sunken", anchor="w",
                  padding=6).pack(fill="x", side="bottom")

    # ---------- common helpers ----------
    def parse_numbers(self, text, integer=False):
        parts = text.replace(",", " ").split()
        if not parts:
            raise ValueError("Enter at least one number.")
        return [int(x) if integer else float(x) for x in parts]

    def save_history(self, entry):
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")

    def show_result(self, widget, text):
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        self.status.set("Calculation completed.")

    def make_output(self, parent):
        out = tk.Text(parent, height=7, wrap="word", font=("Consolas", 11))
        out.pack(fill="both", expand=True, pady=(8, 0))
        return out

    # ---------- Arithmetic ----------
    def make_arithmetic_tab(self):
        tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(tab, text="Arithmetic")

        card = ttk.LabelFrame(tab, text="Arithmetic & Advanced Calculations", style="Card.TLabelframe")
        card.pack(fill="both", expand=True)

        ttk.Label(card, text="Numbers (space or comma separated):").pack(anchor="w")
        nums = tk.StringVar()
        ttk.Entry(card, textvariable=nums, width=60).pack(fill="x", pady=5)

        ttk.Label(card, text="Operation:").pack(anchor="w", pady=(10, 2))
        operation = tk.StringVar(value="Addition")
        combo = ttk.Combobox(
            card, textvariable=operation, state="readonly",
            values=[
                "Addition", "Subtraction", "Multiplication", "Division",
                "Trigonometry", "Square Root", "Cube Root", "Factorial", "Logarithm"
            ]
        )
        combo.pack(fill="x")

        extra_frame = ttk.Frame(card)
        extra_frame.pack(fill="x", pady=8)

        extra_label = ttk.Label(extra_frame, text="")
        extra_entry_var = tk.StringVar()
        extra_entry = ttk.Entry(extra_frame, textvariable=extra_entry_var, width=25)

        trig_var = tk.StringVar(value="sin")
        trig_box = ttk.Combobox(
            extra_frame, textvariable=trig_var, state="readonly",
            values=["sin", "cos", "tan", "cosec", "sec", "cot"], width=15
        )

        result = self.make_output(card)

        def refresh_extra(*_):
            for w in extra_frame.winfo_children():
                w.pack_forget()

            op = operation.get()

            if op in ("Subtraction", "Division"):
                extra_label.config(text="Subtrahend / Divisor:")
                extra_label.pack(side="left")
                extra_entry.pack(side="left", padx=10)

            elif op == "Trigonometry":
                ttk.Label(extra_frame, text="Function:").pack(side="left")
                trig_box.pack(side="left", padx=10)
                ttk.Label(extra_frame, text="Angles are in degrees").pack(side="left", padx=10)

            elif op == "Logarithm":
                extra_label.config(text="Base:")
                extra_label.pack(side="left")
                extra_entry.pack(side="left", padx=10)
                extra_entry_var.set("10")

        operation.trace_add("write", refresh_extra)
        refresh_extra()

        def calculate():
            try:
                values = self.parse_numbers(nums.get())
                op = operation.get()

                if op == "Addition":
                    ans = sum(values)
                    text = f"SUM = {ans}"

                elif op == "Subtraction":
                    if not extra_entry_var.get().strip():
                        raise ValueError("Enter the subtrahend.")
                    d = float(extra_entry_var.get())
                    ans = [x - d for x in values]
                    text = "DIFFERENCES = " + ", ".join(map(str, ans))

                elif op == "Multiplication":
                    ans = math.prod(values)
                    text = f"MULTIPLIED VALUE = {ans}"

                elif op == "Division":
                    if not extra_entry_var.get().strip():
                        raise ValueError("Enter the divisor.")
                    d = float(extra_entry_var.get())
                    if d == 0:
                        raise ValueError("Divisor cannot be zero.")
                    ans = [round(x / d, 3) for x in values]
                    text = "DIVIDED VALUES = " + ", ".join(map(str, ans))

                elif op == "Trigonometry":
                    fn = trig_var.get()
                    ans = []
                    for angle in values:
                        rad = math.radians(angle)
                        if fn == "sin":
                            value = math.sin(rad)
                        elif fn == "cos":
                            value = math.cos(rad)
                        elif fn == "tan":
                            value = math.tan(rad)
                        elif fn == "cosec":
                            s = math.sin(rad)
                            if abs(s) < 1e-12:
                                raise ValueError(f"cosec({angle}°) is undefined.")
                            value = 1 / s
                        elif fn == "sec":
                            c = math.cos(rad)
                            if abs(c) < 1e-12:
                                raise ValueError(f"sec({angle}°) is undefined.")
                            value = 1 / c
                        else:
                            t = math.tan(rad)
                            if abs(t) < 1e-12:
                                raise ValueError(f"cot({angle}°) is undefined.")
                            value = 1 / t
                        # Remove floating-point noise near zero.
                        if abs(value) < 1e-12:
                            value = 0.0
                        ans.append(round(value, 3))
                    text = f"{fn.upper()} VALUES\n\n" + "\n".join(
                        f"{angle}°  =  {value}" for angle, value in zip(values, ans)
                    )

                elif op == "Square Root":
                    ans = []
                    for x in values:
                        if x < 0:
                            raise ValueError("Square root of a negative number is not real.")
                        ans.append(round(math.sqrt(x), 6))
                    text = "SQUARE ROOTS\n\n" + "\n".join(
                        f"√{x} = {y}" for x, y in zip(values, ans)
                    )

                elif op == "Cube Root":
                    ans = [round(math.copysign(abs(x) ** (1 / 3), x), 6) for x in values]
                    text = "CUBE ROOTS\n\n" + "\n".join(
                        f"∛{x} = {y}" for x, y in zip(values, ans)
                    )

                elif op == "Factorial":
                    ans = []
                    for x in values:
                        if x < 0 or not x.is_integer():
                            raise ValueError("Factorial is defined here only for non-negative integers.")
                        ans.append(math.factorial(int(x)))
                    text = "FACTORIALS\n\n" + "\n".join(
                        f"{int(x)}! = {y}" for x, y in zip(values, ans)
                    )

                elif op == "Logarithm":
                    if not extra_entry_var.get().strip():
                        raise ValueError("Enter the logarithm base.")
                    base = float(extra_entry_var.get())
                    if base <= 0 or base == 1:
                        raise ValueError("Logarithm base must be positive and cannot be 1.")
                    ans = []
                    for x in values:
                        if x <= 0:
                            raise ValueError("Logarithm is defined here only for positive numbers.")
                        ans.append(round(math.log(x, base), 6))
                    text = f"LOGARITHMS (BASE {base})\n\n" + "\n".join(
                        f"log_{base}({x}) = {y}" for x, y in zip(values, ans)
                    )

                self.show_result(result, text)
                self.save_history(f"{op} | Inputs: {values} | {text.replace(chr(10), ' | ')}")

            except Exception as e:
                messagebox.showerror("Calculation error", str(e))

        ttk.Button(card, text="Calculate", command=calculate).pack(pady=10, anchor="e")

    # ---------- Statistics ----------
    def make_statistics_tab(self):
        tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(tab, text="Statistics")
        card = ttk.LabelFrame(tab, text="Statistical Calculator", style="Card.TLabelframe")
        card.pack(fill="both", expand=True)

        values = tk.StringVar()
        ttk.Label(card, text="Numbers (space/comma separated):").pack(anchor="w")
        ttk.Entry(card, textvariable=values).pack(fill="x", pady=5)

        choice = tk.StringVar(value="Mean")
        ttk.Label(card, text="Statistic:").pack(anchor="w", pady=(10, 2))
        ttk.Combobox(card, textvariable=choice, state="readonly",
                     values=["Median", "Mean", "Mode", "Variance", "Standard Deviation"]).pack(fill="x")
        result = self.make_output(card)

        def calculate():
            try:
                data = self.parse_numbers(values.get(), integer=True)
                ch = choice.get()
                if ch == "Median":
                    ans = statistics.median(data)
                elif ch == "Mean":
                    ans = statistics.mean(data)
                elif ch == "Mode":
                    ans = statistics.mode(data)
                elif ch == "Variance":
                    if len(data) < 2:
                        raise ValueError("Variance requires at least two values.")
                    ans = statistics.variance(data)
                else:
                    if len(data) < 2:
                        raise ValueError("Standard deviation requires at least two values.")
                    ans = statistics.stdev(data)
                text = f"{ch}: {ans}"
                self.show_result(result, text)
                self.save_history(f"Statistics | Data: {data} -> {ans}")
            except Exception as e:
                messagebox.showerror("Invalid input", str(e))

        ttk.Button(card, text="Calculate", command=calculate).pack(pady=10, anchor="e")

    # ---------- Converters ----------
    def make_converter_tab(self):
        tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(tab, text="Converters")

        card = ttk.LabelFrame(tab, text="Unit & Currency Conversion", style="Card.TLabelframe")
        card.pack(fill="both", expand=True)

        category = tk.StringVar(value="Length")
        ttk.Label(card, text="Category:").pack(anchor="w")
        cat = ttk.Combobox(card, textvariable=category, state="readonly",
                           values=["Length", "Mass", "Temperature", "Time", "INR Currency"])
        cat.pack(fill="x", pady=5)

        controls = ttk.Frame(card)
        controls.pack(fill="x", pady=10)

        source_unit = tk.StringVar()
        target_unit = tk.StringVar()
        amount = tk.StringVar()

        ttk.Label(controls, text="From:").grid(row=0, column=0, sticky="w", padx=4)
        from_box = ttk.Combobox(controls, textvariable=source_unit, state="readonly", width=25)
        from_box.grid(row=1, column=0, sticky="ew", padx=4)
        ttk.Label(controls, text="To:").grid(row=0, column=1, sticky="w", padx=4)
        to_box = ttk.Combobox(controls, textvariable=target_unit, state="readonly", width=25)
        to_box.grid(row=1, column=1, sticky="ew", padx=4)
        ttk.Label(controls, text="Value(s):").grid(row=0, column=2, sticky="w", padx=4)
        ttk.Entry(controls, textvariable=amount).grid(row=1, column=2, sticky="ew", padx=4)
        controls.columnconfigure(0, weight=1)
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(2, weight=2)

        result = self.make_output(card)

        prefixes = {
            "pico": 1e-12, "nano": 1e-9, "micro": 1e-6, "milli": 1e-3,
            "centi": 1e-2, "deci": 1e-1, "base": 1,
            "deca": 1e1, "hecto": 1e2, "kilo": 1e3, "mega": 1e6,
            "giga": 1e9, "tera": 1e12
        }
        currencies = self.load_rates()

        def update_units(*_):
            c = category.get()
            if c in ("Length", "Mass"):
                vals = list(prefixes.keys())
            elif c == "Temperature":
                vals = ["Celsius", "Fahrenheit"]
            elif c == "Time":
                vals = ["Seconds", "Minutes", "Hours"]
            else:
                vals = ["INR"] + [f"{k} ({v[1]})" for k, v in currencies.items()]
            from_box["values"] = vals
            to_box["values"] = vals
            if vals:
                source_unit.set(vals[0])
                target_unit.set(vals[1] if len(vals) > 1 else vals[0])

        category.trace_add("write", update_units)
        update_units()

        def convert():
            try:
                vals = self.parse_numbers(amount.get())
                c = category.get()
                s, t = source_unit.get(), target_unit.get()

                if c in ("Length", "Mass"):
                    ans = [round(x * prefixes[s] / prefixes[t], 8) for x in vals]
                elif c == "Temperature":
                    if s == t:
                        ans = vals
                    elif s == "Celsius":
                        ans = [round(x * 9 / 5 + 32, 4) for x in vals]
                    else:
                        ans = [round((x - 32) * 5 / 9, 4) for x in vals]
                elif c == "Time":
                    seconds = {"Seconds": 1, "Minutes": 60, "Hours": 3600}
                    ans = [round(x * seconds[s] / seconds[t], 6) for x in vals]
                else:
                    scode = s.split()[0]
                    tcode = t.split()[0]
                    if scode == tcode:
                        ans = vals
                    elif scode == "INR":
                        ans = [round(x / currencies[tcode][0], 4) for x in vals]
                    elif tcode == "INR":
                        ans = [round(x * currencies[scode][0], 4) for x in vals]
                    else:
                        # rates file gives INR value per one unit of each foreign currency.
                        ans = [round(x * currencies[scode][0] / currencies[tcode][0], 4) for x in vals]

                text = f"{s} → {t}\n\n" + "\n".join(f"{x}  →  {y}" for x, y in zip(vals, ans))
                self.show_result(result, text)
                self.save_history(f"Converter | {s} -> {t} | Inputs: {vals} | Outputs: {ans}")
            except Exception as e:
                messagebox.showerror("Conversion error", str(e))

        ttk.Button(card, text="Convert", command=convert).pack(pady=10, anchor="e")

    def load_rates(self):
        rates = {}
        path = Path(RATES_FILE)
        if not path.exists():
            return rates
        for line in path.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) >= 3:
                code = parts[0].upper()
                country = parts[1].replace("_", " ")
                number = "".join(c for c in parts[2] if c.isdigit() or c == ".")
                if number:
                    rates[code] = (float(number), country)
        return rates

    # ---------- Finance ----------
    def make_finance_tab(self):
        tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(tab, text="Finance")
        card = ttk.LabelFrame(tab, text="Interest Calculator", style="Card.TLabelframe")
        card.pack(fill="both", expand=True)

        kind = tk.StringVar(value="Simple Interest")
        ttk.Label(card, text="Interest Type:").pack(anchor="w")
        ttk.Combobox(card, textvariable=kind, state="readonly",
                     values=["Simple Interest", "Compound Interest"]).pack(fill="x", pady=5)

        frame = ttk.Frame(card)
        frame.pack(fill="x", pady=12)
        principal, rate, time = tk.StringVar(), tk.StringVar(), tk.StringVar()
        for i, (label, var) in enumerate([("Principal", principal), ("Rate (%)", rate), ("Time", time)]):
            ttk.Label(frame, text=label).grid(row=0, column=i, sticky="w", padx=5)
            ttk.Entry(frame, textvariable=var).grid(row=1, column=i, sticky="ew", padx=5)
            frame.columnconfigure(i, weight=1)

        result = self.make_output(card)

        def calculate():
            try:
                p, r, t = float(principal.get()), float(rate.get()), float(time.get())
                if kind.get() == "Simple Interest":
                    interest = p * r * t / 100
                    total = p + interest
                else:
                    total = p * ((1 + r / 100) ** t)
                    interest = total - p
                text = f"{kind.get()}\nInterest = {interest:.4f}\nTotal Amount = {total:.4f}"
                self.show_result(result, text)
                self.save_history(f"{kind.get()} | Principal: {p}, Rate: {r}, Time: {t} -> Interest: {interest}, Total: {total}")
            except Exception as e:
                messagebox.showerror("Invalid input", str(e))

        ttk.Button(card, text="Calculate", command=calculate).pack(anchor="e")

    # ---------- Geometry ----------
    def make_geometry_tab(self):
        tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(tab, text="Geometry")

        card = ttk.LabelFrame(tab, text="2D & 3D Geometry", style="Card.TLabelframe")
        card.pack(fill="both", expand=True)

        dim = tk.StringVar(value="2D")
        ttk.Label(card, text="Dimension:").pack(anchor="w")
        ttk.Combobox(card, textvariable=dim, state="readonly",
                     values=["2D", "3D"]).pack(fill="x", pady=5)

        shape = tk.StringVar()
        shape_box = ttk.Combobox(card, textvariable=shape, state="readonly")
        shape_box.pack(fill="x", pady=5)

        input_frame = ttk.Frame(card)
        input_frame.pack(fill="x", pady=8)
        result = self.make_output(card)

        fields = []

        def update_shapes(*_):
            vals = ["Square", "Triangle", "Rectangle", "Circle", "Parallelogram", "Trapezium"] if dim.get() == "2D" else [
                "Cube", "Cuboid", "Cylinder", "Sphere", "Cone", "Hemisphere"
            ]
            shape_box["values"] = vals
            shape.set(vals[0])
            rebuild()

        def rebuild(*_):
            for w in input_frame.winfo_children():
                w.destroy()
            fields.clear()
            specs = {
                "Square": ["Side"], "Triangle": ["Side 1", "Side 2", "Side 3"],
                "Rectangle": ["Length", "Breadth"], "Circle": ["Radius"],
                "Parallelogram": ["Base", "Height"], "Trapezium": ["Base 1", "Base 2", "Height"],
                "Cube": ["Side"], "Cuboid": ["Length", "Breadth", "Height"],
                "Cylinder": ["Radius", "Height"], "Sphere": ["Radius"],
                "Cone": ["Radius", "Height"], "Hemisphere": ["Radius"]
            }
            for i, label in enumerate(specs.get(shape.get(), [])):
                var = tk.StringVar()
                ttk.Label(input_frame, text=label).grid(row=0, column=i, sticky="w", padx=4)
                ttk.Entry(input_frame, textvariable=var).grid(row=1, column=i, sticky="ew", padx=4)
                input_frame.columnconfigure(i, weight=1)
                fields.append(var)

        dim.trace_add("write", update_shapes)
        shape_box.bind("<<ComboboxSelected>>", rebuild)
        update_shapes()

        def calculate():
            try:
                x = [float(v.get()) for v in fields]
                s = shape.get()
                if any(v < 0 for v in x):
                    raise ValueError("Measurements cannot be negative.")
                if s == "Square":
                    a, p = x[0] ** 2, 4 * x[0]
                    text = f"Area = {a}\nPerimeter = {p}"
                elif s == "Triangle":
                    a, b, c = x
                    sem = (a+b+c)/2
                    rad = sem*(sem-a)*(sem-b)*(sem-c)
                    if rad <= 0: raise ValueError("These sides do not form a valid triangle.")
                    text = f"Area = {math.sqrt(rad)}\nPerimeter = {a+b+c}"
                elif s == "Rectangle":
                    l,b = x; text = f"Area = {l*b}\nPerimeter = {2*(l+b)}"
                elif s == "Circle":
                    r=x[0]; text = f"Area = {math.pi*r*r:.3f}\nCircumference = {2*math.pi*r:.3f}"
                elif s == "Parallelogram":
                    b,h=x; text = f"Area = {b*h}"
                elif s == "Trapezium":
                    b1,b2,h=x; text = f"Area = {0.5*(b1+b2)*h:.3f}"
                elif s == "Cube":
                    a=x[0]; text = f"Volume = {a**3}\nTotal Surface Area = {6*a*a}"
                elif s == "Cuboid":
                    l,b,h=x; text = f"Volume = {l*b*h}\nTotal Surface Area = {2*(l*b+b*h+h*l)}"
                elif s == "Cylinder":
                    r,h=x; text = f"Volume = {math.pi*r*r*h:.3f}\nTotal Surface Area = {2*math.pi*r*(r+h):.3f}"
                elif s == "Sphere":
                    r=x[0]; text = f"Volume = {4*math.pi*r**3/3:.3f}\nTotal Surface Area = {4*math.pi*r*r:.3f}"
                elif s == "Cone":
                    r,h=x; sl=math.sqrt(r*r+h*h)
                    text = f"Slant Height = {sl:.3f}\nVolume = {math.pi*r*r*h/3:.3f}\nTotal Surface Area = {math.pi*r*(r+sl):.3f}"
                else:
                    r=x[0]
                    text = f"Volume = {2*math.pi*r**3/3:.3f}\nCurved Surface Area = {2*math.pi*r*r:.3f}\nTotal Surface Area = {3*math.pi*r*r:.3f}"
                self.show_result(result, text)
                self.save_history(f"Geometry | {s} | {text.replace(chr(10), ' | ')}")
            except Exception as e:
                messagebox.showerror("Geometry error", str(e))

        ttk.Button(card, text="Calculate", command=calculate).pack(anchor="e", pady=8)

    # ---------- Extra ----------
    def make_extra_tab(self):
        tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(tab, text="Extra")

        card = ttk.LabelFrame(tab, text="Quadratic Equation & BMI", style="Card.TLabelframe")
        card.pack(fill="both", expand=True)

        mode = tk.StringVar(value="Quadratic Equation")
        ttk.Combobox(card, textvariable=mode, state="readonly",
                     values=["Quadratic Equation", "BMI Calculator"]).pack(fill="x", pady=5)

        inputs = ttk.Frame(card)
        inputs.pack(fill="x", pady=10)
        result = self.make_output(card)

        vars_ = [tk.StringVar() for _ in range(3)]

        def rebuild(*_):
            for w in inputs.winfo_children(): w.destroy()
            if mode.get() == "Quadratic Equation":
                labels = ["Coefficient a", "Coefficient b", "Constant c"]
            else:
                labels = ["Weight (kg)", "Height (m)", ""]
            for i, label in enumerate(labels):
                if not label: continue
                ttk.Label(inputs, text=label).grid(row=0, column=i, sticky="w", padx=5)
                ttk.Entry(inputs, textvariable=vars_[i]).grid(row=1, column=i, sticky="ew", padx=5)
                inputs.columnconfigure(i, weight=1)

        mode.trace_add("write", rebuild)
        rebuild()

        def calculate():
            try:
                if mode.get() == "Quadratic Equation":
                    a,b,c = [float(v.get()) for v in vars_]
                    if a == 0: raise ValueError("Coefficient a cannot be zero.")
                    d = b*b - 4*a*c
                    if d > 0:
                        r1=(-b+math.sqrt(d))/(2*a); r2=(-b-math.sqrt(d))/(2*a)
                        text=f"Discriminant = {d}\nRoot 1 = {r1}\nRoot 2 = {r2}\nRoots are real and different."
                    elif d == 0:
                        r=-b/(2*a); text=f"Discriminant = 0\nRoot = {r}\nRoots are real and equal."
                    else:
                        text=f"Discriminant = {d}\nRoots are imaginary."
                    self.save_history(f"Quadratic | a={a}, b={b}, c={c} | {text.replace(chr(10), ' | ')}")
                else:
                    w,h = float(vars_[0].get()), float(vars_[1].get())
                    if h <= 0: raise ValueError("Height must be greater than zero.")
                    bmi=round(w/(h*h),2)
                    category = "Underweight" if bmi<18.5 else "Normal Weight" if bmi<=24.9 else "Overweight" if bmi<29.9 else "Obesity"
                    text=f"BMI = {bmi}\nCategory = {category}"
                    self.save_history(f"BMI | Weight={w}, Height={h} | BMI={bmi} | {category}")
                self.show_result(result, text)
            except Exception as e:
                messagebox.showerror("Calculation error", str(e))

        ttk.Button(card, text="Calculate", command=calculate).pack(anchor="e")

    # ---------- History ----------
    def view_history(self):
        win = tk.Toplevel(self.root)
        win.title("Calculation History")
        win.geometry("800x500")
        text = tk.Text(win, wrap="word", font=("Consolas", 10))
        text.pack(fill="both", expand=True, padx=10, pady=10)
        path = Path(HISTORY_FILE)
        if path.exists() and path.read_text(encoding="utf-8").strip():
            text.insert("1.0", path.read_text(encoding="utf-8"))
        else:
            text.insert("1.0", "NO HISTORY FOUND YET.")
        text.config(state="disabled")

    def clear_history(self):
        if messagebox.askyesno("Clear history", "Delete all calculation history?"):
            Path(HISTORY_FILE).write_text("", encoding="utf-8")
            self.status.set("History cleared successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorGUI(root)
    root.mainloop()
