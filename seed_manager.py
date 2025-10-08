# seed_manager.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
import datetime

CSV_FILE = "seed_list.csv"

COLUMNS = [
    "Name", "Type", "Life Cycle", "Germination (days)",
    "Seed Spacing (inches)", "Temperature (F)", "Seed Depth (inches)",
    "Approximate Start Date", "Transplant Timeframe (weeks)",
    "Time to Maturity", "Heirloom (Y/N)", "Season/s",
    "Benefits", "Uses", "Pairings", "Seed Started Date",
    "Location", "Transplant Date", "Harvest Date", "Issues", "Comments"
]

# Modern color palette
COLORS = {
    'bg_dark': '#1a1a1a',
    'bg_medium': '#242424',
    'bg_light': '#2d2d2d',
    'accent': '#00d9ff',      # Aqua
    'accent_hover': '#00b8d4',
    'success': '#4ade80',     # Light green
    'text': '#e0e0e0',
    'text_dim': '#a0a0a0',
    'border': '#3d3d3d',
    'input_bg': '#1e1e1e',
    'input_focus': '#0a4d5c',
    'warn': '#f59e0b'
}

# Columns that are considered long-text (open in popup on double-click)
LONG_TEXT_COLUMNS = {"Comments", "Benefits", "Uses", "Issues", "Pairings"}

class SeedManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌿 Seed Manager")
        self.root.geometry("1400x820")
        self.root.configure(bg=COLORS['bg_dark'])

        self.data = self.load_or_create_csv()
        self.filtered_data = self.data.copy()

        self.setup_styles()

        # storage for widgets & state
        self.entries = {}
        self.form_vars = {}          # StringVar / stateful combobox variables
        self.multi_values = {}       # For lists like approx start dates and seed started dates
        self.season_vars = {}        # season checkboxes
        self.selected_index = None

        self.setup_ui()
        self.refresh_table()
        self.update_name_dropdown()

    # ---------- persistence ----------
    def load_or_create_csv(self):
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        else:
            # create blank file with headers
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=COLUMNS)
                writer.writeheader()
            return []

    def save_to_csv(self):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(self.data)

    # ---------- styles ----------
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Treeview styling tuned to show clearer column separation in dark theme
        style.configure("Treeview",
                        background=COLORS['bg_medium'],
                        foreground=COLORS['text'],
                        fieldbackground=COLORS['bg_medium'],
                        rowheight=28,
                        bordercolor=COLORS['border'],
                        borderwidth=1)
        style.map('Treeview', background=[('selected', COLORS['accent'])], foreground=[('selected', COLORS['bg_dark'])])

        # Heading: slightly raised with accent text so headings visually separate columns
        style.configure("Treeview.Heading",
                        background=COLORS['bg_light'],
                        foreground=COLORS['accent'],
                        relief='raised',
                        font=('Segoe UI', 9, 'bold'),
                        borderwidth=1)
        style.map("Treeview.Heading", background=[('active', COLORS['accent_hover'])])

        # Combobox (force dark list colors via option_add)
        style.configure("TCombobox",
                        fieldbackground=COLORS['input_bg'],
                        foreground=COLORS['text'])

        # Apply general option_add for popups / listboxes inside combobox
        self.root.option_add('*TCombobox*Listbox.background', COLORS['input_bg'])
        self.root.option_add('*TCombobox*Listbox.foreground', COLORS['text'])
        self.root.option_add('*TCombobox*Listbox.selectBackground', COLORS['accent'])
        self.root.option_add('*TCombobox*Listbox.selectForeground', COLORS['bg_dark'])

        # Checkbutton style
        style.configure("TCheckbutton", background=COLORS['bg_medium'], foreground=COLORS['text'])

    # ---------- small helpers ----------
    def create_modern_button(self, parent, text, command, bg_color=None, width=None):
        if bg_color is None:
            bg_color = COLORS['bg_light']
        btn = tk.Button(parent, text=text, command=command,
                        bg=bg_color, fg=COLORS['text'],
                        font=('Segoe UI', 9, 'bold'),
                        relief='flat', padx=12, pady=6,
                        cursor='hand2', borderwidth=0, width=width)
        def on_enter(e):
            btn['bg'] = COLORS['accent_hover']
        def on_leave(e):
            btn['bg'] = bg_color
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def create_entry(self, parent, width=20):
        e = tk.Entry(parent, bg=COLORS['input_bg'], fg=COLORS['text'],
                     insertbackground=COLORS['accent'], font=('Segoe UI', 10), relief='flat', width=width)
        return e

    def create_dropdown(self, parent, var, values, width=12):
        cb = ttk.Combobox(parent, textvariable=var, values=values, width=width, font=('Segoe UI', 9))
        if values:
            cb.set(values[0])
        return cb

    # ---------- UI layout ----------
    def setup_ui(self):
        # header
        header = tk.Frame(self.root, bg=COLORS['bg_dark'], height=64)
        header.pack(fill='x', padx=16, pady=(8,6))
        tk.Label(header, text="🌿 SEED MANAGER", font=('Segoe UI', 20, 'bold'),
                 bg=COLORS['bg_dark'], fg=COLORS['accent']).pack(side='left')
        tk.Label(header, text="Organize • Track • Grow", font=('Segoe UI', 10),
                 bg=COLORS['bg_dark'], fg=COLORS['text_dim']).pack(side='left', padx=12, pady=6)

        # toolbar: name dropdown + save/save as + filters
        toolbar = tk.Frame(self.root, bg=COLORS['bg_medium'])
        toolbar.pack(fill='x', padx=16, pady=(0,10))

        # Name selection for quick edit
        tk.Label(toolbar, text="Edit:", bg=COLORS['bg_medium'], fg=COLORS['text_dim']).pack(side='left', padx=(6,4))
        self.name_var = tk.StringVar()
        self.name_dropdown = ttk.Combobox(toolbar, textvariable=self.name_var, values=[], width=32)
        self.name_dropdown.pack(side='left', padx=(0,8))
        self.name_dropdown.bind("<<ComboboxSelected>>", self.on_name_select)

        # Save button (explicit)
        save_btn = self.create_modern_button(toolbar, "💾 Save", self.manual_save, bg_color=COLORS['accent'], width=10)
        save_btn.pack(side='left', padx=6)
        save_as_btn = self.create_modern_button(toolbar, "Save As", self.save_as, bg_color=COLORS['bg_light'], width=10)
        save_as_btn.pack(side='left', padx=6)

        # Right-side filter controls (kept compact)
        filter_frame = tk.Frame(toolbar, bg=COLORS['bg_medium'])
        filter_frame.pack(side='right', padx=6)

        # Pairings filter - now built from individual comma-separated items across all rows
        tk.Label(filter_frame, text="Pairing:", bg=COLORS['bg_medium'], fg=COLORS['text_dim']).pack(side='left', padx=(4,4))
        self.pairing_var = tk.StringVar()
        # initial values set in update_name_dropdown()
        self.pairing_dd = ttk.Combobox(filter_frame, textvariable=self.pairing_var, values=[], width=18)
        self.pairing_dd.pack(side='left', padx=(0,6))
        self.pairing_dd.bind("<<ComboboxSelected>>", lambda e: self.filter_pairing())

        tk.Label(filter_frame, text="Season:", bg=COLORS['bg_medium'], fg=COLORS['text_dim']).pack(side='left', padx=(4,4))
        seasons = sorted(set([r.get("Season/s", "") for r in self.data if r.get("Season/s")]))
        self.season_filter_var = tk.StringVar()
        self.season_dd = ttk.Combobox(filter_frame, textvariable=self.season_filter_var, values=seasons, width=14)
        self.season_dd.pack(side='left', padx=(0,6))
        self.season_dd.bind("<<ComboboxSelected>>", lambda e: self.filter_season())

        reset_btn = self.create_modern_button(filter_frame, "⟲ Reset", self.reset_filters)
        reset_btn.pack(side='left', padx=4)

        # main area: table + form stacked
        main_area = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main_area.pack(fill='both', expand=True, padx=16, pady=(0,16))

        # Table container at top
        table_container = tk.Frame(main_area, bg=COLORS['border'])
        table_container.pack(fill='both', expand=True, pady=(0,12))

        # Treeview — keep headings, tuned widths
        self.tree = ttk.Treeview(table_container, columns=COLUMNS, show='headings')
        for col in COLUMNS:
            self.tree.heading(col, text=col)
            width = 180 if col == "Name" else 140
            # setting a small minwidth and enabling stretch keeps the columns separated visually
            self.tree.column(col, width=width, anchor='w', minwidth=80, stretch=True)
        self.tree.pack(side='left', fill='both', expand=True)

        yscroll = ttk.Scrollbar(table_container, orient='vertical', command=self.tree.yview)
        yscroll.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=yscroll.set)

        xscroll = ttk.Scrollbar(main_area, orient='horizontal', command=self.tree.xview)
        xscroll.pack(fill='x')
        self.tree.configure(xscrollcommand=xscroll.set)

        # Double-click behavior: if user double-clicks a long-text column cell -> open popup, otherwise load into form
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # form area below table
        form_frame_outer = tk.Frame(main_area, bg=COLORS['bg_dark'])
        form_frame_outer.pack(fill='x', pady=(6,0))

        form_frame = tk.LabelFrame(form_frame_outer, text=" Add / Edit Seed (double-click row to load)", bg=COLORS['bg_medium'],
                                   fg=COLORS['accent'], font=('Segoe UI', 10, 'bold'), labelanchor='n', padx=12, pady=8)
        form_frame.pack(fill='x')

        # create form grid (4 columns of inputs)
        months = [str(i).zfill(2) for i in range(1,13)]
        days = [str(i).zfill(2) for i in range(1,32)]
        years = [str(y) for y in range(datetime.datetime.now().year, datetime.datetime.now().year + 6)]
        temps = [str(i) for i in range(0, 101)]
        depths = [f"{i/2:.1f}" for i in range(0, 21)]  # 0.0 .. 10.0
        # Transplant timeframe now increments by 1 from 1 to 20 (per request)
        transplant_weeks = [str(i) for i in range(1, 21)]
        maturity_days = [str(i) for i in range(0, 301)]

        for i, col in enumerate(COLUMNS):
            row = i // 4
            colpos = (i % 4) * 2

            lbl = tk.Label(form_frame, text=col, bg=COLORS['bg_medium'], fg=COLORS['text_dim'], font=('Segoe UI', 9, 'bold'))
            lbl.grid(row=row, column=colpos, sticky='w', padx=(4,6), pady=6)

            # special inputs
            widget = None

            # lifecycle
            if col == "Life Cycle":
                var = tk.StringVar()
                self.form_vars[col] = var
                widget = ttk.Combobox(form_frame, textvariable=var, values=["Annual", "Perennial"], width=18)
                widget.set("Annual")

            # Heirloom as dropdown
            elif col == "Heirloom (Y/N)":
                var = tk.StringVar()
                self.form_vars[col] = var
                widget = ttk.Combobox(form_frame, textvariable=var, values=["Yes", "No", "Unknown"], width=12)
                widget.set("Unknown")

            # Season checkboxes (multiple)
            elif col == "Season/s":
                frm = tk.Frame(form_frame, bg=COLORS['bg_medium'])
                frm.grid(row=row, column=colpos+1, sticky='w', padx=(0,12), pady=6)
                seasons_list = ["Spring", "Summer", "Autumn", "Winter"]
                for s in seasons_list:
                    sv = tk.BooleanVar(value=False)
                    cb = ttk.Checkbutton(frm, text=s, variable=sv)
                    cb.pack(side='left', padx=(0,6))
                    self.season_vars[s] = sv
                widget = frm  # placeholder frame already placed

            # Temperature range (min/max)
            elif col == "Temperature (F)":
                frm = tk.Frame(form_frame, bg=COLORS['bg_medium'])
                frm.grid(row=row, column=colpos+1, sticky='w', padx=(0,12), pady=6)
                vmin = tk.StringVar(); vmax = tk.StringVar()
                self.form_vars["TempMin"] = vmin
                self.form_vars["TempMax"] = vmax
                cb1 = ttk.Combobox(frm, textvariable=vmin, values=temps, width=6)
                cb2 = ttk.Combobox(frm, textvariable=vmax, values=temps, width=6)
                cb1.pack(side='left'); tk.Label(frm, text="–", bg=COLORS['bg_medium'], fg=COLORS['text']).pack(side='left', padx=4); cb2.pack(side='left')
                widget = frm

            # Seed Depth dropdown
            elif col == "Seed Depth (inches)":
                var = tk.StringVar()
                self.form_vars[col] = var
                widget = ttk.Combobox(form_frame, textvariable=var, values=depths, width=10)
                widget.set(depths[0])

            # Approximate Start Date (allow multiple month/day entries)
            elif col == "Approximate Start Date":
                frm = tk.Frame(form_frame, bg=COLORS['bg_medium'])
                frm.grid(row=row, column=colpos+1, sticky='w', padx=(0,12), pady=6)
                # month/day dropdowns + add button + display
                mvar = tk.StringVar(); dvar = tk.StringVar()
                mcb = ttk.Combobox(frm, textvariable=mvar, values=months, width=5)
                dcb = ttk.Combobox(frm, textvariable=dvar, values=days, width=5)
                mcb.set(months[0]); dcb.set(days[0])
                add_btn = self.create_modern_button(frm, "+", lambda c="Approximate Start Date", mv=mvar, dv=dvar: self.add_multi_date(c, mv.get(), dv.get()), bg_color=COLORS['bg_light'], width=2)
                display = tk.Label(frm, text="", bg=COLORS['bg_medium'], fg=COLORS['text'], anchor='w', width=24)
                mcb.pack(side='left'); tk.Label(frm, text="/", bg=COLORS['bg_medium'], fg=COLORS['text']).pack(side='left'); dcb.pack(side='left'); add_btn.pack(side='left', padx=6); display.pack(side='left', padx=8)
                self.multi_values["Approximate Start Date"] = {"values": [], "display": display}
                widget = frm

            # Transplant Timeframe (weeks) dropdown (1..20)
            elif col == "Transplant Timeframe (weeks)":
                var = tk.StringVar(); self.form_vars[col] = var
                widget = ttk.Combobox(form_frame, textvariable=var, values=transplant_weeks, width=10)
                widget.set(transplant_weeks[0])

            # Time to Maturity as range (min-max days)
            elif col == "Time to Maturity":
                frm = tk.Frame(form_frame, bg=COLORS['bg_medium'])
                frm.grid(row=row, column=colpos+1, sticky='w', padx=(0,12), pady=6)
                tmin = tk.StringVar(); tmax = tk.StringVar()
                self.form_vars["MaturityMin"] = tmin
                self.form_vars["MaturityMax"] = tmax
                cb1 = ttk.Combobox(frm, textvariable=tmin, values=maturity_days, width=6)
                cb2 = ttk.Combobox(frm, textvariable=tmax, values=maturity_days, width=6)
                cb1.pack(side='left'); tk.Label(frm, text="–", bg=COLORS['bg_medium'], fg=COLORS['text']).pack(side='left', padx=4); cb2.pack(side='left')
                widget = frm

            # Seed Started Date - allow multiple mm/dd/yyyy values
            elif col == "Seed Started Date":
                frm = tk.Frame(form_frame, bg=COLORS['bg_medium'])
                frm.grid(row=row, column=colpos+1, sticky='w', padx=(0,12), pady=6)
                sv_m = tk.StringVar(); sv_d = tk.StringVar(); sv_y = tk.StringVar()
                months2 = months; days2 = days; years2 = years
                mcb = ttk.Combobox(frm, textvariable=sv_m, values=months2, width=4)
                dcb = ttk.Combobox(frm, textvariable=sv_d, values=days2, width=4)
                ycb = ttk.Combobox(frm, textvariable=sv_y, values=years2, width=6)
                mcb.set(months2[0]); dcb.set(days2[0]); ycb.set(years2[0])
                add_btn = self.create_modern_button(frm, "+", lambda c="Seed Started Date", mv=sv_m, dv=sv_d, yv=sv_y: self.add_multi_date(c, mv.get(), dv.get(), yv.get()), bg_color=COLORS['bg_light'], width=2)
                display = tk.Label(frm, text="", bg=COLORS['bg_medium'], fg=COLORS['text'], anchor='w', width=22)
                mcb.pack(side='left'); tk.Label(frm, text="/", bg=COLORS['bg_medium'], fg=COLORS['text']).pack(side='left'); dcb.pack(side='left'); tk.Label(frm, text="/", bg=COLORS['bg_medium'], fg=COLORS['text']).pack(side='left'); ycb.pack(side='left', padx=(4,6)); add_btn.pack(side='left'); display.pack(side='left', padx=6)
                self.multi_values["Seed Started Date"] = {"values": [], "display": display}
                widget = frm

            # Transplant Date & Harvest Date - single mm/dd/yyyy entry (string) using simple entry (you can type or use pattern)
            elif col in ("Transplant Date", "Harvest Date"):
                widget = self.create_entry(form_frame, width=18)

            # Pairings, Uses, Benefits, Issues, Comments are textareas
            elif col in ("Comments", "Benefits", "Uses", "Issues", "Pairings"):
                # Pairings may be typed in as comma-separated string; keep as single-line text widget but allow multiple words
                # We'll treat Pairings as a text entry (single-line) to match previous behavior in CSV and to avoid layout change
                if col == "Pairings":
                    # use Entry for Pairings to keep it compact (but allow long text)
                    ent = self.create_entry(form_frame, width=28)
                    widget = ent
                else:
                    txt = tk.Text(form_frame, height=2, width=28, bg=COLORS['input_bg'], fg=COLORS['text'], insertbackground=COLORS['accent'])
                    widget = txt

            else:
                # default entry (Name, Type, Germination, Spacing, Location, Pairings)
                widget = self.create_entry(form_frame, width=22)

            # if widget not already gridded (some were)
            if col not in ("Season/s", "Approximate Start Date", "Seed Started Date"):
                # many special widgets were already placed; put remaining ones
                if widget is not None:
                    widget.grid(row=row, column=colpos+1, sticky='w', padx=(0,12), pady=6)

            self.entries[col] = widget

        # action buttons
        action_frame = tk.Frame(form_frame, bg=COLORS['bg_dark'])
        action_frame.grid(row=20, column=0, columnspan=8, pady=(12,4))

        add_btn = self.create_modern_button(action_frame, "➕ ADD / UPDATE", self.add_or_update_entry, bg_color=COLORS['success'])
        add_btn.pack(side='left', padx=8)
        del_btn = self.create_modern_button(action_frame, "🗑 DELETE", self.delete_entry, bg_color='#ef4444')
        del_btn.pack(side='left', padx=8)
        clear_btn = self.create_modern_button(action_frame, "✖ CLEAR", self.clear_form)
        clear_btn.pack(side='left', padx=8)
        export_btn = self.create_modern_button(action_frame, "💾 EXPORT CSV", self.export_csv, bg_color=COLORS['accent'])
        export_btn.pack(side='left', padx=8)

    # ---------- multi-date helper ----------
    def add_multi_date(self, column_name, month, day, year=None):
        # month/day pair or month/day/year if year given
        if not month or not day:
            return
        if year:
            s = f"{month}/{day}/{year}"
        else:
            s = f"{month}/{day}"
        mv = self.multi_values.get(column_name)
        if mv is None:
            return
        # avoid duplicates
        if s not in mv['values']:
            mv['values'].append(s)
            mv['display'].config(text=", ".join(mv['values']))

    # ---------- UI helpers ----------
    def update_name_dropdown(self):
        names = [r.get("Name", "") for r in self.data if r.get("Name", "")]
        names_unique = sorted(list(dict.fromkeys(names)))  # keep order unique
        self.name_dropdown['values'] = names_unique

        # pairings: build from split items (comma-separated) across all rows
        pairing_items = set()
        for r in self.data:
            p = r.get("Pairings", "")
            if p:
                parts = [part.strip() for part in p.split(',') if part.strip()]
                for part in parts:
                    pairing_items.add(part)
        pairings_sorted = sorted(pairing_items, key=lambda s: s.lower())
        self.pairing_dd['values'] = pairings_sorted

        seasons = sorted(set([r.get("Season/s", "") for r in self.data if r.get("Season/s")]))
        self.season_dd['values'] = seasons

    # ---------- filters & sorts ----------
    def sort_by_name(self):
        self.filtered_data = sorted(self.filtered_data, key=lambda r: r.get("Name", "").lower())
        self.refresh_table()

    def sort_by_type(self):
        self.filtered_data = sorted(self.filtered_data, key=lambda r: r.get("Type", "").lower())
        self.refresh_table()

    def filter_heirloom(self):
        self.filtered_data = [r for r in self.data if r.get("Heirloom (Y/N)", "").lower() in ("y", "yes")]
        self.refresh_table()

    def filter_pairing(self):
        val = self.pairing_var.get().strip().lower()
        if not val:
            return
        # include rows where any of the comma-separated pairings matches the selected item
        def row_has_pairing(row):
            p = row.get("Pairings", "")
            if not p:
                return False
            parts = [part.strip().lower() for part in p.split(',') if part.strip()]
            return val in parts
        self.filtered_data = [r for r in self.data if row_has_pairing(r)]
        self.refresh_table()

    def filter_season(self):
        val = self.season_filter_var.get().strip().lower()
        if not val:
            return
        self.filtered_data = [r for r in self.data if val in r.get("Season/s", "").lower()]
        self.refresh_table()

    def reset_filters(self):
        self.pairing_var.set('')
        self.season_filter_var.set('')
        self.filtered_data = self.data.copy()
        self.refresh_table()

    # ---------- table/form linking ----------
    def refresh_table(self):
        # empty tree
        for row in self.tree.get_children():
            self.tree.delete(row)
        # insert filtered rows
        for r in self.filtered_data:
            values = [r.get(col, "") for col in COLUMNS]
            self.tree.insert('', 'end', values=values)
        self.update_name_dropdown()

    def on_name_select(self, event=None):
        name = self.name_var.get()
        if not name:
            return
        # find first occurrence and load
        for idx, row in enumerate(self.data):
            if row.get("Name", "") == name:
                self.selected_index = idx
                self.load_row_into_form(row)
                break

    def on_tree_double_click(self, event):
        # identify which row and column were clicked
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)  # returns like '#1', '#2' etc
        if not row_id or not col_id:
            return
        try:
            col_index = int(col_id.replace('#', '')) - 1
        except:
            col_index = None

        if col_index is not None and 0 <= col_index < len(COLUMNS):
            col_name = COLUMNS[col_index]
            values = self.tree.item(row_id, 'values')
            cell_value = ""
            if col_index < len(values):
                cell_value = values[col_index] or ""

            # If the clicked column is a long-text column, open a popup to show full text (wrapped)
            if col_name in LONG_TEXT_COLUMNS:
                self.open_text_popup(col_name, cell_value)
                return

        # otherwise default behavior: load the whole selected row into form (preserve old behavior)
        # select the row and call load_selected_to_form
        self.tree.selection_set(row_id)
        self.load_selected_to_form()

    def open_text_popup(self, title, text):
        # simple dark-themed popup to show/wrap the full text of a cell
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.configure(bg=COLORS['bg_dark'])
        popup.geometry("700x320")
        popup.transient(self.root)
        popup.grab_set()

        lbl = tk.Label(popup, text=title, bg=COLORS['bg_dark'], fg=COLORS['accent'], font=('Segoe UI', 11, 'bold'))
        lbl.pack(anchor='w', padx=12, pady=(12,6))

        txt = tk.Text(popup, wrap='word', bg=COLORS['bg_medium'], fg=COLORS['text'], insertbackground=COLORS['accent'])
        txt.pack(fill='both', expand=True, padx=12, pady=(0,12))

        # insert text and make read-only
        txt.insert('1.0', text)
        txt.configure(state='disabled')

        # a close button
        btn = self.create_modern_button(popup, "Close", lambda: popup.destroy(), bg_color=COLORS['bg_light'], width=10)
        btn.pack(pady=(0,12))

    def on_tree_right_click(self, event):
        # reserved if you want context menu later; not currently used
        pass

    def load_selected_to_form(self):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], 'values')
        # build row dict to pass
        row = {}
        for i, col in enumerate(COLUMNS):
            if i < len(vals):
                row[col] = vals[i]
            else:
                row[col] = ""
        # set selected_index to index in data if name matches
        name = row.get("Name", "")
        for idx, r in enumerate(self.data):
            if r.get("Name", "") == name:
                self.selected_index = idx
                break
        self.load_row_into_form(row)

    def load_row_into_form(self, row):
        # clear form first
        self.clear_form()

        for col in COLUMNS:
            val = row.get(col, "")
            widget = self.entries.get(col)
            if col in ("Comments", "Benefits", "Uses", "Issues"):
                if widget:
                    widget.delete("1.0", tk.END)
                    widget.insert("1.0", val)
            elif col == "Pairings":
                # Pairings stored as comma-separated string in an Entry
                w = self.entries.get(col)
                if isinstance(w, tk.Entry):
                    w.delete(0, tk.END)
                    w.insert(0, val)
            elif col == "Season/s":
                # val can be comma separated
                selected = [s.strip() for s in val.split(',') if s.strip()]
                for s, var in self.season_vars.items():
                    var.set(s in selected)
            elif col == "Temperature (F)":
                # expect "min-max"
                try:
                    mn, mx = val.split('-', 1)
                    self.form_vars["TempMin"].set(mn)
                    self.form_vars["TempMax"].set(mx)
                except:
                    self.form_vars["TempMin"].set('')
                    self.form_vars["TempMax"].set('')
            elif col == "Time to Maturity":
                try:
                    mn, mx = val.split('-', 1)
                    self.form_vars["MaturityMin"].set(mn)
                    self.form_vars["MaturityMax"].set(mx)
                except:
                    self.form_vars["MaturityMin"].set('')
                    self.form_vars["MaturityMax"].set('')
            elif col == "Seed Depth (inches)":
                if val and self.form_vars.get(col) is not None:
                    self.form_vars[col].set(val)
            elif col == "Life Cycle":
                if val and self.form_vars.get(col) is not None:
                    self.form_vars[col].set(val)
            elif col == "Heirloom (Y/N)":
                if val and self.form_vars.get(col) is not None:
                    self.form_vars[col].set(val)
            elif col == "Approximate Start Date":
                # comma-separated list of mm/dd or mm/dd/yyyy
                mv = self.multi_values.get("Approximate Start Date")
                if mv:
                    vals = [p.strip() for p in val.split(',') if p.strip()]
                    mv['values'] = vals
                    mv['display'].config(text=", ".join(vals))
            elif col == "Seed Started Date":
                mv = self.multi_values.get("Seed Started Date")
                if mv:
                    vals = [p.strip() for p in val.split(',') if p.strip()]
                    mv['values'] = vals
                    mv['display'].config(text=", ".join(vals))
            else:
                # default entry or text
                w = self.entries.get(col)
                if isinstance(w, tk.Entry):
                    w.delete(0, tk.END); w.insert(0, val)
                elif isinstance(w, tk.Text):
                    w.delete("1.0", tk.END); w.insert("1.0", val)

        # set name dropdown
        if row.get("Name"):
            self.name_var.set(row.get("Name"))

    # ---------- add / update / delete ----------
    def add_or_update_entry(self):
        new = {}
        # gather form data
        for col in COLUMNS:
            if col in ("Comments", "Benefits", "Uses", "Issues"):
                w = self.entries[col]
                new[col] = w.get("1.0", tk.END).strip()
            elif col == "Pairings":
                w = self.entries.get(col)
                if isinstance(w, tk.Entry):
                    new[col] = w.get().strip()
                else:
                    new[col] = ""
            elif col == "Season/s":
                sel = [s for s, v in self.season_vars.items() if v.get()]
                new[col] = ", ".join(sel)
            elif col == "Temperature (F)":
                mn = self.form_vars.get("TempMin", tk.StringVar()).get()
                mx = self.form_vars.get("TempMax", tk.StringVar()).get()
                new[col] = f"{mn}-{mx}" if mn and mx else (mn or mx or "")
            elif col == "Time to Maturity":
                mn = self.form_vars.get("MaturityMin", tk.StringVar()).get()
                mx = self.form_vars.get("MaturityMax", tk.StringVar()).get()
                new[col] = f"{mn}-{mx}" if mn and mx else (mn or mx or "")
            elif col == "Seed Depth (inches)":
                new[col] = self.form_vars.get(col, tk.StringVar()).get() or ""
            elif col == "Life Cycle":
                new[col] = self.form_vars.get("Life Cycle", tk.StringVar()).get() or ""
            elif col == "Heirloom (Y/N)":
                new[col] = self.form_vars.get("Heirloom (Y/N)", tk.StringVar()).get() or ""
            elif col == "Approximate Start Date":
                mv = self.multi_values.get("Approximate Start Date", {"values": []})
                new[col] = ", ".join(mv.get("values", []))
            elif col == "Seed Started Date":
                mv = self.multi_values.get("Seed Started Date", {"values": []})
                new[col] = ", ".join(mv.get("values", []))
            else:
                w = self.entries.get(col)
                if isinstance(w, tk.Entry):
                    new[col] = w.get().strip()
                elif isinstance(w, ttk.Combobox):
                    new[col] = w.get().strip()
                else:
                    new[col] = ""

        if not new.get("Name"):
            messagebox.showwarning("Validation", "Name is required.")
            return

        # find existing by name and update, else append
        found = False
        for i, row in enumerate(self.data):
            if row.get("Name", "") == new["Name"]:
                self.data[i] = new
                found = True
                break
        if not found:
            self.data.append(new)

        # persist and refresh
        self.save_to_csv()
        self.reset_filters()
        self.refresh_table()
        self.update_name_dropdown()
        messagebox.showinfo("Saved", f"Saved '{new['Name']}'")
        self.clear_form()

    def delete_entry(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a row to delete.")
            return
        name = self.tree.item(sel[0], 'values')[0]
        if messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            self.data = [r for r in self.data if r.get("Name", "") != name]
            self.save_to_csv()
            self.reset_filters()
            self.refresh_table()
            self.update_name_dropdown()
            messagebox.showinfo("Deleted", f"Deleted '{name}'")

    def manual_save(self):
        # Save current form content without clearing
        # will add/update like add_or_update_entry but keep fields
        new = {}
        for col in COLUMNS:
            if col in ("Comments", "Benefits", "Uses", "Issues"):
                w = self.entries[col]
                new[col] = w.get("1.0", tk.END).strip()
            elif col == "Pairings":
                w = self.entries.get(col)
                if isinstance(w, tk.Entry):
                    new[col] = w.get().strip()
                else:
                    new[col] = ""
            elif col == "Season/s":
                sel = [s for s, v in self.season_vars.items() if v.get()]
                new[col] = ", ".join(sel)
            elif col == "Temperature (F)":
                mn = self.form_vars.get("TempMin", tk.StringVar()).get()
                mx = self.form_vars.get("TempMax", tk.StringVar()).get()
                new[col] = f"{mn}-{mx}" if mn and mx else (mn or mx or "")
            elif col == "Time to Maturity":
                mn = self.form_vars.get("MaturityMin", tk.StringVar()).get()
                mx = self.form_vars.get("MaturityMax", tk.StringVar()).get()
                new[col] = f"{mn}-{mx}" if mn and mx else (mn or mx or "")
            elif col == "Seed Depth (inches)":
                new[col] = self.form_vars.get(col, tk.StringVar()).get() or ""
            elif col == "Life Cycle":
                new[col] = self.form_vars.get("Life Cycle", tk.StringVar()).get() or ""
            elif col == "Heirloom (Y/N)":
                new[col] = self.form_vars.get("Heirloom (Y/N)", tk.StringVar()).get() or ""
            elif col == "Approximate Start Date":
                mv = self.multi_values.get("Approximate Start Date", {"values": []})
                new[col] = ", ".join(mv.get("values", []))
            elif col == "Seed Started Date":
                mv = self.multi_values.get("Seed Started Date", {"values": []})
                new[col] = ", ".join(mv.get("values", []))
            else:
                w = self.entries.get(col)
                if isinstance(w, tk.Entry):
                    new[col] = w.get().strip()
                elif isinstance(w, ttk.Combobox):
                    new[col] = w.get().strip()
                else:
                    new[col] = ""

        if not new.get("Name"):
            messagebox.showwarning("Validation", "Name is required to save.")
            return

        # update or create
        found = False
        for i, row in enumerate(self.data):
            if row.get("Name", "") == new["Name"]:
                self.data[i] = new
                found = True
                break
        if not found:
            self.data.append(new)

        self.save_to_csv()
        self.reset_filters()
        self.refresh_table()
        self.update_name_dropdown()
        messagebox.showinfo("Saved", f"Saved '{new['Name']}'")

    # ---------- export ----------
    def export_csv(self):
        f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not f:
            return
        with open(f, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.DictWriter(fh, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(self.data)
        messagebox.showinfo("Exported", f"Exported to {f}")

    # ---------- save as ----------
    def save_as(self):
        f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not f:
            return
        with open(f, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.DictWriter(fh, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(self.data)
        messagebox.showinfo("Saved", f"Saved to {f}")

    # ---------- helpers ----------
    def clear_form(self):
        # clear entries and multi-values
        for col, w in self.entries.items():
            if isinstance(w, tk.Entry):
                w.delete(0, tk.END)
            elif isinstance(w, tk.Text):
                w.delete("1.0", tk.END)
            # comboboxes handled via form_vars
        for v in self.form_vars.values():
            try:
                v.set('')
            except:
                pass
        for mv in self.multi_values.values():
            mv['values'] = []
            mv['display'].config(text='')
        for sv in self.season_vars.values():
            sv.set(False)
        self.selected_index = None
        self.name_var.set('')

# ---------- main ----------
def main():
    root = tk.Tk()
    app = SeedManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
