# seed_manager.py  — Modernized UI (dark / "Spotify-ish" look)
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

COLORS = {
    'bg_dark': '#0f1416',
    'bg_medium': '#121617',
    'bg_light': '#1f2628',
    'accent': '#1db954',      # spotify-like green
    'accent_hover': '#16a34a',
    'success': '#4ade80',
    'text': '#e6eef2',
    'text_dim': '#9aa6ab',
    'border': '#20282a',
    'input_bg': '#0f1416',
    'input_focus': '#133a2b',
    'warn': '#f59e0b',
    'danger': '#ef4444'
}

LONG_TEXT_COLUMNS = {"Comments", "Benefits", "Uses", "Issues", "Pairings"}

class SeedManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌿 Seed Manager")
        # set a modern minimum and allow user to resize
        self.root.geometry("1400x820")
        self.root.minsize(1100, 700)
        self.root.configure(bg=COLORS['bg_dark'])

        self.data = self.load_or_create_csv()
        self.filtered_data = self.data.copy()

        self.setup_styles()

        self.entries = {}
        self.form_vars = {}
        self.multi_values = {}
        self.season_vars = {}
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
        # choose clam which gives us more skinning control
        style.theme_use('clam')

        style.configure("Treeview",
                        background=COLORS['bg_medium'],
                        foreground=COLORS['text'],
                        fieldbackground=COLORS['bg_medium'],
                        rowheight=28,
                        bordercolor=COLORS['border'],
                        borderwidth=0,
                        font=('Segoe UI', 10))
        style.map('Treeview', background=[('selected', COLORS['accent'])], foreground=[('selected', COLORS['bg_dark'])])

        style.configure("Treeview.Heading",
                        background=COLORS['bg_light'],
                        foreground=COLORS['accent'],
                        relief='flat',
                        font=('Segoe UI', 10, 'bold'),
                        borderwidth=0)
        style.map("Treeview.Heading", background=[('active', COLORS['accent_hover'])])

        style.configure("TCombobox",
                        fieldbackground=COLORS['input_bg'],
                        foreground=COLORS['text'],
                        background=COLORS['input_bg'],
                        arrowcolor=COLORS['text'])

        style.configure("TButton",
                        background=COLORS['bg_light'],
                        foreground=COLORS['text'],
                        borderwidth=0,
                        focusthickness=0,
                        padding=6,
                        font=('Segoe UI', 9, 'bold'))

        style.configure("TLabel", background=COLORS['bg_dark'], foreground=COLORS['text'])

        self.root.option_add('*TCombobox*Listbox.background', COLORS['input_bg'])
        self.root.option_add('*TCombobox*Listbox.foreground', COLORS['text'])
        self.root.option_add('*TCombobox*Listbox.selectBackground', COLORS['accent'])
        self.root.option_add('*TCombobox*Listbox.selectForeground', COLORS['bg_dark'])

        style.configure("TCheckbutton", background=COLORS['bg_medium'], foreground=COLORS['text'])

    # ---------- small helpers ----------
    def create_modern_button(self, parent, text, command, bg_color=None, width=None):
        if bg_color is None:
            bg_color = COLORS['bg_light']
        btn = tk.Button(parent, text=text, command=command,
                        bg=bg_color, fg=COLORS['text'],
                        font=('Segoe UI', 9, 'bold'),
                        relief='flat', padx=12, pady=6,
                        cursor='hand2', borderwidth=0, width=width, activebackground=COLORS['accent_hover'])
        def on_enter(e):
            # subtle brighten effect
            btn['bg'] = COLORS['accent_hover'] if bg_color == COLORS['accent'] else '#2a3234'
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
        # top container: left sidebar + main content
        top = tk.Frame(self.root, bg=COLORS['bg_dark'])
        top.pack(fill='both', expand=True)

        # left sidebar
        sidebar = tk.Frame(top, bg=COLORS['bg_light'], width=220)
        sidebar.pack(side='left', fill='y', padx=(16,8), pady=16)
        sidebar.pack_propagate(False)

        # app badge
        badge = tk.Label(sidebar, text="🌿\nSeedManager", bg=COLORS['bg_light'], fg=COLORS['text'], font=('Segoe UI', 16, 'bold'), justify='center')
        badge.pack(pady=(18,6))

        caption = tk.Label(sidebar, text="Organize • Track • Grow", bg=COLORS['bg_light'], fg=COLORS['text_dim'], font=('Segoe UI', 9))
        caption.pack(pady=(0,12))

        # quick actions in sidebar
        sb_actions = tk.Frame(sidebar, bg=COLORS['bg_light'])
        sb_actions.pack(pady=(8,12), fill='x', padx=12)

        btn_quick_add = self.create_modern_button(sb_actions, "➕ New Seed", lambda: self.clear_form(), bg_color=COLORS['accent'])
        btn_quick_add.pack(fill='x', pady=(0,8))
        btn_export = self.create_modern_button(sb_actions, "💾 Export CSV", self.export_csv, bg_color=COLORS['bg_dark'])
        btn_export.pack(fill='x', pady=(0,8))

        # small hint
        hint = tk.Label(sidebar, text="Tip: double-click rows to edit or view long text", bg=COLORS['bg_light'], fg=COLORS['text_dim'], wraplength=180, font=('Segoe UI', 9))
        hint.pack(padx=12, pady=(8,8))

        # search / filters section in sidebar
        search_frame = tk.LabelFrame(sidebar, text="Search & Filters", bg=COLORS['bg_light'], fg=COLORS['text'], font=('Segoe UI', 10, 'bold'))
        search_frame.pack(fill='x', padx=12, pady=(8,12))

        tk.Label(search_frame, text="Search name:", bg=COLORS['bg_light'], fg=COLORS['text_dim'], font=('Segoe UI', 9)).pack(anchor='w', padx=8, pady=(6,0))
        self.search_var = tk.StringVar()
        search_entry = self.create_entry(search_frame, width=20)
        search_entry.configure(textvariable=self.search_var)
        search_entry.pack(padx=8, pady=(4,8), fill='x')
        # live search
        self.search_var.trace_add("write", lambda *a: self.live_search())

        tk.Label(search_frame, text="Filter pairing:", bg=COLORS['bg_light'], fg=COLORS['text_dim'], font=('Segoe UI', 9)).pack(anchor='w', padx=8, pady=(4,0))
        self.pairing_var = tk.StringVar()
        self.pairing_dd = ttk.Combobox(search_frame, textvariable=self.pairing_var, values=[], width=20)
        self.pairing_dd.pack(padx=8, pady=(4,8))
        self.pairing_dd.bind("<<ComboboxSelected>>", lambda e: self.filter_pairing())

        tk.Label(search_frame, text="Filter season:", bg=COLORS['bg_light'], fg=COLORS['text_dim'], font=('Segoe UI', 9)).pack(anchor='w', padx=8, pady=(4,0))
        self.season_filter_var = tk.StringVar()
        self.season_dd = ttk.Combobox(search_frame, textvariable=self.season_filter_var, values=[], width=20)
        self.season_dd.pack(padx=8, pady=(4,8))
        self.season_dd.bind("<<ComboboxSelected>>", lambda e: self.filter_season())

        reset_btn = self.create_modern_button(search_frame, "⟲ Reset Filters", self.reset_filters, bg_color=COLORS['bg_dark'])
        reset_btn.pack(padx=8, pady=(6,12), fill='x')

        # main content area
        main_area = tk.Frame(top, bg=COLORS['bg_dark'])
        main_area.pack(side='left', fill='both', expand=True, padx=(8,16), pady=16)

        # header (within main area)
        header = tk.Frame(main_area, bg=COLORS['bg_dark'])
        header.pack(fill='x', pady=(0,10))

        title = tk.Label(header, text="🌿 SEED MANAGER", font=('Segoe UI', 18, 'bold'),
                         bg=COLORS['bg_dark'], fg=COLORS['accent'])
        title.pack(side='left')

        sub = tk.Label(header, text="Your seeds, organized", font=('Segoe UI', 10),
                       bg=COLORS['bg_dark'], fg=COLORS['text_dim'])
        sub.pack(side='left', padx=12)

        # toolbar: name dropdown + save + save as + sort
        toolbar = tk.Frame(header, bg=COLORS['bg_dark'])
        toolbar.pack(side='right')

        tk.Label(toolbar, text="Edit:", bg=COLORS['bg_dark'], fg=COLORS['text_dim']).pack(side='left', padx=(6,4))
        self.name_var = tk.StringVar()
        self.name_dropdown = ttk.Combobox(toolbar, textvariable=self.name_var, values=[], width=32)
        self.name_dropdown.pack(side='left', padx=(0,8))
        self.name_dropdown.bind("<<ComboboxSelected>>", self.on_name_select)

        save_btn = self.create_modern_button(toolbar, "💾 Save", self.manual_save, bg_color=COLORS['accent'])
        save_btn.pack(side='left', padx=6)
        save_as_btn = self.create_modern_button(toolbar, "Save As", self.save_as, bg_color=COLORS['bg_light'])
        save_as_btn.pack(side='left', padx=6)

        # Table container
        table_container = tk.Frame(main_area, bg=COLORS['border'])
        table_container.pack(fill='both', expand=True)

        # Treeview
        self.tree = ttk.Treeview(table_container, columns=COLUMNS, show='headings', selectmode='browse')
        # add striped row tags
        self.tree.tag_configure('oddrow', background=COLORS['bg_medium'])
        self.tree.tag_configure('evenrow', background='#0d1516')  # slightly darker
        for col in COLUMNS:
            self.tree.heading(col, text=col)
            width = 200 if col == "Name" else 140
            self.tree.column(col, width=width, anchor='w', minwidth=80, stretch=True)
        self.tree.pack(side='left', fill='both', expand=True)

        yscroll = ttk.Scrollbar(table_container, orient='vertical', command=self.tree.yview)
        yscroll.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=yscroll.set)

        xscroll = ttk.Scrollbar(main_area, orient='horizontal', command=self.tree.xview)
        xscroll.pack(fill='x')
        self.tree.configure(xscrollcommand=xscroll.set)

        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # form area below table
        form_frame_outer = tk.Frame(main_area, bg=COLORS['bg_dark'])
        form_frame_outer.pack(fill='x', pady=(12,0))

        form_frame = tk.LabelFrame(form_frame_outer, text=" Add / Edit Seed (double-click row to load)", bg=COLORS['bg_medium'],
                                   fg=COLORS['accent'], font=('Segoe UI', 10, 'bold'), labelanchor='n', padx=12, pady=8)
        form_frame.pack(fill='x')

        # create form grid (4 columns)
        months = [str(i).zfill(2) for i in range(1,13)]
        days = [str(i).zfill(2) for i in range(1,32)]
        years = [str(y) for y in range(datetime.datetime.now().year, datetime.datetime.now().year + 6)]
        temps = [str(i) for i in range(0, 101)]
        depths = [f"{i/2:.1f}" for i in range(0, 21)]
        transplant_weeks = [str(i) for i in range(1, 21)]
        maturity_days = [str(i) for i in range(0, 301)]

        for i, col in enumerate(COLUMNS):
            row = i // 4
            colpos = (i % 4) * 2

            lbl = tk.Label(form_frame, text=col, bg=COLORS['bg_medium'], fg=COLORS['text_dim'], font=('Segoe UI', 9, 'bold'))
            lbl.grid(row=row, column=colpos, sticky='w', padx=(4,6), pady=6)

            widget = None

            if col == "Life Cycle":
                var = tk.StringVar()
                self.form_vars[col] = var
                widget = ttk.Combobox(form_frame, textvariable=var, values=["Annual", "Perennial"], width=18)
                widget.set("Annual")

            elif col == "Heirloom (Y/N)":
                var = tk.StringVar()
                self.form_vars[col] = var
                widget = ttk.Combobox(form_frame, textvariable=var, values=["Yes", "No", "Unknown"], width=12)
                widget.set("Unknown")

            elif col == "Season/s":
                frm = tk.Frame(form_frame, bg=COLORS['bg_medium'])
                frm.grid(row=row, column=colpos+1, sticky='w', padx=(0,12), pady=6)
                seasons_list = ["Spring", "Summer", "Autumn", "Winter"]
                for s in seasons_list:
                    sv = tk.BooleanVar(value=False)
                    cb = ttk.Checkbutton(frm, text=s, variable=sv)
                    cb.pack(side='left', padx=(0,6))
                    self.season_vars[s] = sv
                widget = frm

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

            elif col == "Seed Depth (inches)":
                var = tk.StringVar()
                self.form_vars[col] = var
                widget = ttk.Combobox(form_frame, textvariable=var, values=depths, width=10)
                widget.set(depths[0])

            elif col == "Approximate Start Date":
                frm = tk.Frame(form_frame, bg=COLORS['bg_medium'])
                frm.grid(row=row, column=colpos+1, sticky='w', padx=(0,12), pady=6)
                mvar = tk.StringVar(); dvar = tk.StringVar()
                mcb = ttk.Combobox(frm, textvariable=mvar, values=months, width=5)
                dcb = ttk.Combobox(frm, textvariable=dvar, values=days, width=5)
                mcb.set(months[0]); dcb.set(days[0])
                add_btn = self.create_modern_button(frm, "+", lambda c="Approximate Start Date", mv=mvar, dv=dvar: self.add_multi_date(c, mv.get(), dv.get()), bg_color=COLORS['bg_light'], width=2)
                display = tk.Label(frm, text="", bg=COLORS['bg_medium'], fg=COLORS['text'], anchor='w', width=24)
                mcb.pack(side='left'); tk.Label(frm, text="/", bg=COLORS['bg_medium'], fg=COLORS['text']).pack(side='left'); dcb.pack(side='left'); add_btn.pack(side='left', padx=6); display.pack(side='left', padx=8)
                self.multi_values["Approximate Start Date"] = {"values": [], "display": display}
                widget = frm

            elif col == "Transplant Timeframe (weeks)":
                var = tk.StringVar(); self.form_vars[col] = var
                widget = ttk.Combobox(form_frame, textvariable=var, values=transplant_weeks, width=10)
                widget.set(transplant_weeks[0])

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

            elif col in ("Transplant Date", "Harvest Date"):
                widget = self.create_entry(form_frame, width=18)

            elif col in ("Comments", "Benefits", "Uses", "Issues", "Pairings"):
                if col == "Pairings":
                    ent = self.create_entry(form_frame, width=28)
                    widget = ent
                else:
                    txt = tk.Text(form_frame, height=2, width=28, bg=COLORS['input_bg'], fg=COLORS['text'], insertbackground=COLORS['accent'])
                    widget = txt

            else:
                widget = self.create_entry(form_frame, width=22)

            if col not in ("Season/s", "Approximate Start Date", "Seed Started Date"):
                if widget is not None:
                    widget.grid(row=row, column=colpos+1, sticky='w', padx=(0,12), pady=6)

            self.entries[col] = widget

        # action buttons
        action_frame = tk.Frame(form_frame, bg=COLORS['bg_dark'])
        action_frame.grid(row=20, column=0, columnspan=8, pady=(12,4))

        add_btn = self.create_modern_button(action_frame, "➕ ADD / UPDATE", self.add_or_update_entry, bg_color=COLORS['success'])
        add_btn.pack(side='left', padx=8)
        del_btn = self.create_modern_button(action_frame, "🗑 DELETE", self.delete_entry, bg_color=COLORS['danger'])
        del_btn.pack(side='left', padx=8)
        clear_btn = self.create_modern_button(action_frame, "✖ CLEAR", self.clear_form)
        clear_btn.pack(side='left', padx=8)
        export_btn = self.create_modern_button(action_frame, "💾 EXPORT CSV", self.export_csv, bg_color=COLORS['accent'])
        export_btn.pack(side='left', padx=8)

    # ---------- multi-date helper ----------
    def add_multi_date(self, column_name, month, day, year=None):
        if not month or not day:
            return
        if year:
            s = f"{month}/{day}/{year}"
        else:
            s = f"{month}/{day}"
        mv = self.multi_values.get(column_name)
        if mv is None:
            return
        if s not in mv['values']:
            mv['values'].append(s)
            mv['display'].config(text=", ".join(mv['values']))

    # ---------- UI helpers ----------
    def update_name_dropdown(self):
        names = [r.get("Name", "") for r in self.data if r.get("Name", "")]
        names_unique = sorted(list(dict.fromkeys(names)))
        self.name_dropdown['values'] = names_unique

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

    def live_search(self):
        q = self.search_var.get().strip().lower()
        if not q:
            self.filtered_data = self.data.copy()
        else:
            self.filtered_data = [r for r in self.data if q in r.get("Name", "").lower()]
        self.refresh_table()

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
        self.search_var.set('')
        self.filtered_data = self.data.copy()
        self.refresh_table()

    # ---------- table/form linking ----------
    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for idx, r in enumerate(self.filtered_data):
            values = [r.get(col, "") for col in COLUMNS]
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree.insert('', 'end', values=values, tags=(tag,))
        self.update_name_dropdown()

    def on_name_select(self, event=None):
        name = self.name_var.get()
        if not name:
            return
        for idx, row in enumerate(self.data):
            if row.get("Name", "") == name:
                self.selected_index = idx
                self.load_row_into_form(row)
                break

    def on_tree_double_click(self, event):
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
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
            if col_name in LONG_TEXT_COLUMNS:
                self.open_text_popup(col_name, cell_value)
                return

        self.tree.selection_set(row_id)
        self.load_selected_to_form()

    def open_text_popup(self, title, text):
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
        txt.insert('1.0', text)
        txt.configure(state='disabled')

        btn = self.create_modern_button(popup, "Close", lambda: popup.destroy(), bg_color=COLORS['bg_light'], width=10)
        btn.pack(pady=(0,12))

    def load_selected_to_form(self):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], 'values')
        row = {}
        for i, col in enumerate(COLUMNS):
            if i < len(vals):
                row[col] = vals[i]
            else:
                row[col] = ""
        name = row.get("Name", "")
        for idx, r in enumerate(self.data):
            if r.get("Name", "") == name:
                self.selected_index = idx
                break
        self.load_row_into_form(row)

    def load_row_into_form(self, row):
        self.clear_form()
        for col in COLUMNS:
            val = row.get(col, "")
            widget = self.entries.get(col)
            if col in ("Comments", "Benefits", "Uses", "Issues"):
                if widget:
                    widget.delete("1.0", tk.END)
                    widget.insert("1.0", val)
            elif col == "Pairings":
                w = self.entries.get(col)
                if isinstance(w, tk.Entry):
                    w.delete(0, tk.END)
                    w.insert(0, val)
            elif col == "Season/s":
                selected = [s.strip() for s in val.split(',') if s.strip()]
                for s, var in self.season_vars.items():
                    var.set(s in selected)
            elif col == "Temperature (F)":
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
                w = self.entries.get(col)
                if isinstance(w, tk.Entry):
                    w.delete(0, tk.END); w.insert(0, val)
                elif isinstance(w, tk.Text):
                    w.delete("1.0", tk.END); w.insert("1.0", val)
        if row.get("Name"):
            self.name_var.set(row.get("Name"))

    # ---------- add / update / delete ----------
    def add_or_update_entry(self):
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
            messagebox.showwarning("Validation", "Name is required.")
            return

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
        for col, w in self.entries.items():
            if isinstance(w, tk.Entry):
                w.delete(0, tk.END)
            elif isinstance(w, tk.Text):
                w.delete("1.0", tk.END)
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
