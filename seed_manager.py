import os
import datetime
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, StringVar, BooleanVar, END, ttk

# =========================
# Settings
# =========================
EXPECTED_COLUMNS = [
    "Name", "Type", "Life Cycle", "Germination (days)",
    "Seed Spacing (inches)", "Temperature (F)", "Seed Depth (inches)",
    "Approximate Start Date (mm/yy)", "Transplant Timeframe (weeks)",
    "Time to Maturity (days)", "Heirloom (Y/N)", "Season/s",
    "Benefits", "Uses", "Pairings", "Seed Started Date",
    "Location", "Transplant Date", "Harvest Date", "Issues", "Comments"
]

SEASONS = ["Spring", "Summer", "Autumn", "Winter", "Year-Around"]
DEFAULT_FILE = "seed_list.xlsx"

# =========================
# Colors & Fonts
# =========================
BG_COLOR = "#1e1e1e"
FG_COLOR = "#ffffff"
ENTRY_BG = "#2e2e2e"
ENTRY_FG = "#ffffff"
LABEL_COLOR = "#24EFEF"
BTN_BG = "#539C9C"
BTN_FG = "#ffffff"
TABLE_BG = "#2a2d2e"
TABLE_FG = "#ffffff"
TABLE_HL = "#24EFEF"
FONT_LABEL = ("Arial", 11)
FONT_ENTRY = ("Arial", 11)

# =========================
# Seed Manager Class
# =========================
class SeedManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌱 Seed Manager")
        self.root.configure(bg=BG_COLOR)
        self.filename = DEFAULT_FILE
        self.df = pd.DataFrame(columns=EXPECTED_COLUMNS)
        self.controls = {}
        self.multi_values = {}
        self.selected_index = None

        self.setup_ui()
        self.ensure_default_file()
        self.load_default_file()

    # =========================
    # UI Setup
    # =========================
    def setup_ui(self):
        self.main = tk.Frame(self.root, bg=BG_COLOR)
        self.main.pack(fill="both", expand=True)

        # Top toolbar
        toolbar = tk.Frame(self.main, bg=BG_COLOR)
        toolbar.pack(fill="x", pady=6, padx=8)

        # Dropdown for selecting name to edit
        self.name_var = StringVar()
        self.name_dropdown = ttk.Combobox(toolbar, textvariable=self.name_var, state="readonly")
        self.name_dropdown.pack(side="left", padx=4)
        self.name_dropdown.bind("<<ComboboxSelected>>", self.load_selected_name)

        # Save & Save As buttons with electric hover
        save_btn = tk.Button(toolbar, text="Save", command=self.auto_save, bg=LABEL_COLOR, fg=BTN_FG, font=FONT_LABEL)
        save_btn.pack(side="left", padx=4)
        self.add_electric_hover(save_btn)

        save_as_btn = tk.Button(toolbar, text="Save As", command=self.save_as, bg=BTN_BG, fg=BTN_FG, font=FONT_LABEL)
        save_as_btn.pack(side="left", padx=4)
        self.add_electric_hover(save_as_btn)

        tk.Button(toolbar, text="Help", command=self.show_help, bg=BTN_BG, fg=BTN_FG, font=FONT_LABEL).pack(side="right", padx=4)

        # Content
        content = tk.Frame(self.main, bg=BG_COLOR)
        content.pack(fill="both", expand=True, padx=8, pady=(0,8))

        # Left form
        self.form_frame = tk.Frame(content, bg=BG_COLOR)
        self.form_frame.pack(side="left", fill="y", padx=(0,8), pady=4)
        self.build_form()

        # Form buttons
        btn_frame = tk.Frame(self.form_frame, bg=BG_COLOR)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Clear Form", command=self.clear_form, width=15, bg=BTN_BG, fg=BTN_FG, font=FONT_LABEL).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Delete Selected Row", command=self.delete_selected_row, width=20, bg=BTN_BG, fg=BTN_FG, font=FONT_LABEL).pack(side="left", padx=4)

        # Right: Table
        right_frame = tk.Frame(content, bg=BG_COLOR)
        right_frame.pack(side="left", fill="both", expand=True)
        self.table_frame = tk.Frame(right_frame, bg=BG_COLOR)
        self.table_frame.pack(fill="both", expand=True)

        # Treeview for database
        self.tree = ttk.Treeview(self.table_frame, columns=EXPECTED_COLUMNS, show="headings", selectmode="browse")
        for col in EXPECTED_COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="w")

        # Scrollbars
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True, side="left")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Style Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=TABLE_BG, foreground=TABLE_FG, fieldbackground=TABLE_BG, rowheight=25)
        style.map('Treeview', background=[('selected', TABLE_HL)])

    # =========================
    # Electric hover effect
    # =========================
    def add_electric_hover(self, btn):
        def on_enter(e):
            btn.config(cursor="hand2", bg="#00FFFF")
        def on_leave(e):
            btn.config(cursor="", bg=BTN_BG if btn.cget("text")=="Save As" else LABEL_COLOR)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # =========================
    # Form Build
    # =========================
    def build_form(self):
        self.season_vars = {}
        months = [f"{i:02d}" for i in range(1,13)]
        days = [f"{i:02d}" for i in range(1,32)]
        years = [str(y) for y in range(datetime.datetime.now().year, datetime.datetime.now().year+6)]

        for col in EXPECTED_COLUMNS:
            row = tk.Frame(self.form_frame, bg=BG_COLOR)
            row.pack(fill="x", pady=4, padx=4)
            tk.Label(row, text=col+":", width=20, anchor="w", fg=LABEL_COLOR, bg=BG_COLOR, font=FONT_LABEL).pack(side="left")

            if col == "Heirloom (Y/N)":
                var = StringVar(value="Unknown")
                for val in ["Yes", "No", "Unknown"]:
                    rb = tk.Radiobutton(row, text=val, variable=var, value=val, bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR, font=FONT_LABEL)
                    rb.pack(side="left", padx=2)
                    rb.bind("<ButtonRelease-1>", lambda e: self.auto_save())
                self.controls[col] = var

            elif col == "Season/s":
                season_container = tk.Frame(row, bg=BG_COLOR)
                season_container.pack(side="left", fill="x", expand=True)
                for s in SEASONS:
                    var = BooleanVar(value=False)
                    cb = tk.Checkbutton(season_container, text=s, variable=var, bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR, font=FONT_LABEL)
                    cb.pack(side="top", anchor="w")
                    cb.bind("<ButtonRelease-1>", lambda e: self.auto_save())
                    self.season_vars[s] = var
                self.controls[col] = self.season_vars

            elif col == "Temperature (F)":
                temps = [str(i) for i in range(0, 101, 5)]
                start_cb = ttk.Combobox(row, values=temps, width=5)
                end_cb = ttk.Combobox(row, values=temps, width=5)
                start_cb.pack(side="left")
                tk.Label(row, text="to", fg=FG_COLOR, bg=BG_COLOR, font=FONT_LABEL).pack(side="left", padx=2)
                end_cb.pack(side="left")
                start_cb.bind("<<ComboboxSelected>>", lambda e: self.auto_save())
                end_cb.bind("<<ComboboxSelected>>", lambda e: self.auto_save())
                self.controls[col] = (start_cb, end_cb)

            elif col == "Approximate Start Date (mm/yy)":
                month_cb = ttk.Combobox(row, values=months, width=3)
                year_cb = ttk.Combobox(row, values=years, width=4)
                month_cb.pack(side="left")
                tk.Label(row, text="/", fg=FG_COLOR, bg=BG_COLOR, font=FONT_LABEL).pack(side="left", padx=2)
                year_cb.pack(side="left")
                month_cb.bind("<<ComboboxSelected>>", lambda e: self.auto_save())
                year_cb.bind("<<ComboboxSelected>>", lambda e: self.auto_save())
                self.controls[col] = (month_cb, year_cb)

            elif col in ("Seed Depth (inches)", "Seed Spacing (inches)"):
                ent = tk.Entry(row, width=10, bg=ENTRY_BG, fg=ENTRY_FG, font=FONT_ENTRY)
                ent.pack(side="left")
                ent.bind("<KeyRelease>", lambda e: self.auto_save())
                add_btn = tk.Button(row, text="+", command=lambda c=col: self.add_multi_value(c), bg=BTN_BG, fg=BTN_FG, font=FONT_LABEL)
                add_btn.pack(side="left", padx=2)
                display = tk.Label(row, text="", width=25, anchor="w", fg=FG_COLOR, bg=BG_COLOR, font=FONT_LABEL)
                display.pack(side="left", padx=4)
                self.controls[col] = ent
                self.multi_values[col] = {"values": [], "display": display}

            elif col in ("Seed Started Date", "Transplant Date", "Harvest Date"):
                m_var, d_var, y_var = StringVar(), StringVar(), StringVar()
                m_cb = ttk.Combobox(row, values=months, width=3, textvariable=m_var)
                d_cb = ttk.Combobox(row, values=days, width=3, textvariable=d_var)
                y_cb = ttk.Combobox(row, values=years, width=4, textvariable=y_var)
                m_cb.pack(side="left")
                tk.Label(row, text="/", fg=FG_COLOR, bg=BG_COLOR, font=FONT_LABEL).pack(side="left", padx=2)
                d_cb.pack(side="left")
                tk.Label(row, text="/", fg=FG_COLOR, bg=BG_COLOR, font=FONT_LABEL).pack(side="left", padx=2)
                y_cb.pack(side="left")
                m_var.trace("w", lambda *args: self.auto_save())
                d_var.trace("w", lambda *args: self.auto_save())
                y_var.trace("w", lambda *args: self.auto_save())
                self.controls[col] = (m_var, d_var, y_var)

            elif col == "Comments":
                ent = tk.Text(row, width=25, height=4, bg=ENTRY_BG, fg=ENTRY_FG, font=FONT_ENTRY)
                ent.pack(side="left", fill="x", expand=True)
                ent.bind("<KeyRelease>", lambda e: self.auto_save())
                self.controls[col] = ent

            else:
                ent = tk.Entry(row, width=25, bg=ENTRY_BG, fg=ENTRY_FG, font=FONT_ENTRY)
                ent.pack(side="left", fill="x", expand=True)
                ent.bind("<KeyRelease>", lambda e: self.auto_save())
                self.controls[col] = ent

    # =========================
    # Multi Value Handling
    # =========================
    def add_multi_value(self, column_name):
        ent = self.controls[column_name]
        val = ent.get().strip()
        if not val:
            return
        mv = self.multi_values[column_name]
        mv["values"].append(val)
        mv["display"].configure(text=", ".join(mv["values"]))
        ent.delete(0, END)
        self.auto_save()

    # =========================
    # Auto-save functionality
    # =========================
    def auto_save(self):
        data = self.read_form_values()
        if not data["Name"]:
            return
        # Check if editing existing row
        if self.selected_index is not None:
            for c in EXPECTED_COLUMNS:
                self.df.at[self.selected_index, c] = data[c]
        else:
            if not self.df[(self.df["Name"]==data["Name"])].empty:
                idx = self.df[self.df["Name"]==data["Name"]].index[0]
                for c in EXPECTED_COLUMNS:
                    self.df.at[idx,c] = data[c]
            else:
                self.df = pd.concat([self.df, pd.DataFrame([data])], ignore_index=True)
        self.df.to_excel(self.filename, index=False, engine="openpyxl")
        self.refresh_table()
        self.update_name_dropdown()

    # =========================
    # Load selected name from dropdown
    # =========================
    def load_selected_name(self, event=None):
        name = self.name_var.get()
        if not name:
            return
        idx = self.df[self.df["Name"]==name].index[0]
        self.selected_index = idx
        self.on_tree_select(None)

    # =========================
    # File Handling
    # =========================
    def ensure_default_file(self):
        if not os.path.exists(DEFAULT_FILE):
            pd.DataFrame(columns=EXPECTED_COLUMNS).to_excel(DEFAULT_FILE, index=False, engine="openpyxl")

    def load_default_file(self):
        try:
            df = pd.read_excel(DEFAULT_FILE, engine="openpyxl")
            for c in EXPECTED_COLUMNS:
                if c not in df.columns:
                    df[c] = ""
            self.df = df[EXPECTED_COLUMNS].copy()
        except Exception:
            self.df = pd.DataFrame(columns=EXPECTED_COLUMNS)
        self.refresh_table()
        self.update_name_dropdown()

    def save_as(self):
        f = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
        if f:
            self.df.to_excel(f, index=False, engine="openpyxl")
            self.filename = f
            messagebox.showinfo("Saved", f"Saved to: {os.path.basename(f)}")

    # =========================
    # Update name dropdown
    # =========================
    def update_name_dropdown(self):
        names = self.df["Name"].dropna().unique().tolist()
        self.name_dropdown['values'] = names

    # =========================
    # Form Reading
    # =========================
    def read_form_values(self):
        row = {}
        for col in EXPECTED_COLUMNS:
            ctrl = self.controls[col]
            if col in self.multi_values:
                vals = self.multi_values[col]["values"].copy()
                typed = ctrl.get().strip()
                if typed:
                    vals.append(typed)
                row[col] = ", ".join(vals)
            elif col == "Season/s":
                sel = [s for s, var in ctrl.items() if var.get()]
                row[col] = ", ".join(sel)
            elif col in ("Seed Started Date", "Transplant Date", "Harvest Date"):
                m,d,y = ctrl
                if m.get() and d.get() and y.get():
                    row[col] = f"{m.get()}/{d.get()}/{y.get()}"
                else:
                    row[col] = ""
            elif col == "Temperature (F)":
                s, e = ctrl[0].get(), ctrl[1].get()
                row[col] = f"{s}-{e}" if s and e else s or e
            elif col == "Approximate Start Date (mm/yy)":
                m, y = ctrl[0].get(), ctrl[1].get()
                row[col] = f"{m}/{y}" if m and y else ""
            elif col == "Heirloom (Y/N)":
                row[col] = ctrl.get()
            elif col == "Comments":
                row[col] = ctrl.get("1.0", END).strip()
            else:
                row[col] = ctrl.get().strip()
        return row

    # =========================
    # Treeview Handling
    # =========================
    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for i,row in self.df.iterrows():
            values = [str(row[c]) for c in EXPECTED_COLUMNS]
            self.tree.insert("", "end", iid=str(i), values=values)

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if sel:
            self.selected_index = int(sel[0])
            row = self.df.iloc[self.selected_index]
            for col in EXPECTED_COLUMNS:
                val = str(row[col])
                ctrl = self.controls[col]
                if col in self.multi_values:
                    self.multi_values[col]["values"] = [p.strip() for p in val.split(",") if p.strip()]
                    self.multi_values[col]["display"].configure(text=", ".join(self.multi_values[col]["values"]))
                    ctrl.delete(0, END)
                elif col == "Season/s":
                    for s in SEASONS:
                        ctrl[s].set(s in val)
                elif col == "Temperature (F)":
                    if "-" in val:
                        s,e = val.split("-",1)
                        ctrl[0].set(s.strip())
                        ctrl[1].set(e.strip())
                    else:
                        ctrl[0].set(val)
                        ctrl[1].set("")
                elif col == "Approximate Start Date (mm/yy)":
                    if "/" in val:
                        m,y = val.split("/",1)
                        ctrl[0].set(m.strip())
                        ctrl[1].set(y.strip())
                elif col in ("Seed Started Date", "Transplant Date", "Harvest Date"):
                    if val:
                        try:
                            mm,dd,yy = val.split("/")
                            ctrl[0].set(mm)
                            ctrl[1].set(dd)
                            ctrl[2].set(yy)
                        except:
                            ctrl[0].set("")
                            ctrl[1].set("")
                            ctrl[2].set("")
                elif col == "Heirloom (Y/N)":
                    ctrl.set(val)
                elif col == "Comments":
                    ctrl.delete("1.0", END)
                    ctrl.insert(END, val)
                else:
                    ctrl.delete(0, END)
                    ctrl.insert(0, val)

    # =========================
    # Clear & Delete
    # =========================
    def clear_form(self):
        for col in EXPECTED_COLUMNS:
            ctrl = self.controls[col]
            if col in self.multi_values:
                ctrl.delete(0, END)
                self.multi_values[col]["values"] = []
                self.multi_values[col]["display"].configure(text="")
            elif col == "Season/s":
                for s in SEASONS:
                    ctrl[s].set(False)
            elif col in ("Temperature (F)", "Approximate Start Date (mm/yy)"):
                for c in ctrl:
                    c.set("")
            elif col in ("Seed Started Date", "Transplant Date", "Harvest Date"):
                for c in ctrl:
                    c.set("")
            elif col == "Heirloom (Y/N)":
                ctrl.set("Unknown")
            elif col == "Comments":
                ctrl.delete("1.0", END)
            else:
                ctrl.delete(0, END)
        self.selected_index = None

    def delete_selected_row(self):
        if self.selected_index is not None:
            self.df.drop(index=self.selected_index, inplace=True)
            self.df.reset_index(drop=True, inplace=True)
            self.selected_index = None
            self.refresh_table()
            self.update_name_dropdown()
            self.clear_form()
            self.auto_save()

    # =========================
    # Help
    # =========================
    def show_help(self):
        messagebox.showinfo("Help", "🌱 Seed Manager Instructions:\n\n"
                            "- Fill out the form on the left.\n"
                            "- Multi-values can be added using '+'.\n"
                            "- Save frequently using 'Save' or 'Save As'.\n"
                            "- Select a seed from the dropdown to edit.\n"
                            "- Tree view shows all seeds.\n"
                            "- Use 'Clear Form' or 'Delete Selected Row' as needed.")


# =========================
# Main
# =========================
def main():
    root = tk.Tk()
    root.geometry("1400x800")
    app = SeedManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
