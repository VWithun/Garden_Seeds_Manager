import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os

CSV_FILE = "seed_list.csv"

COLUMNS = [
    "Name", "Type", "Life Cycle", "Germination (days)",
    "Seed Spacing (inches)", "Temperature (F)", "Seed Depth (inches)",
    "Approximate Start Date (mm/yy)", "Transplant Timeframe (weeks)",
    "Time to Maturity (days)", "Heirloom (Y/N)", "Season/s",
    "Benefits", "Uses", "Pairings", "Seed Started Date",
    "Location", "Transplant Date", "Harvest Date", "Issues", "Comments"
]

# Modern color palette
COLORS = {
    'bg_dark': '#1a1a1a',
    'bg_medium': '#242424',
    'bg_light': '#2d2d2d',
    'accent': '#00d9ff',  # Aqua
    'accent_hover': '#00b8d4',
    'success': '#4ade80',  # Light green
    'text': '#e0e0e0',
    'text_dim': '#a0a0a0',
    'border': '#3d3d3d',
    'input_bg': '#1e1e1e',
    'input_focus': '#0a4d5c'
}


class SeedManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌿 Seed Manager")
        self.root.geometry("1400x800")
        self.root.configure(bg=COLORS['bg_dark'])

        self.data = self.load_or_create_csv()
        self.filtered_data = self.data.copy()

        self.setup_styles()
        self.setup_ui()

    def load_or_create_csv(self):
        """Load existing CSV or create a blank one"""
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            return data
        else:
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=COLUMNS)
                writer.writeheader()
            return []

    def save_to_csv(self):
        """Save data to CSV file"""
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(self.data)

    def setup_styles(self):
        """Setup modern ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Treeview style
        style.configure("Treeview",
                       background=COLORS['bg_medium'],
                       foreground=COLORS['text'],
                       fieldbackground=COLORS['bg_medium'],
                       borderwidth=0,
                       rowheight=30)
        style.map('Treeview', background=[('selected', COLORS['accent'])])
        
        # Treeview heading
        style.configure("Treeview.Heading",
                       background=COLORS['bg_light'],
                       foreground=COLORS['accent'],
                       borderwidth=1,
                       relief="flat")
        style.map("Treeview.Heading",
                 background=[('active', COLORS['accent_hover'])])
        
        # Combobox
        style.configure("TCombobox",
                       fieldbackground=COLORS['input_bg'],
                       background=COLORS['bg_light'],
                       foreground=COLORS['text'],
                       borderwidth=1,
                       arrowcolor=COLORS['accent'])

    def create_modern_button(self, parent, text, command, bg_color=None):
        """Create a modern styled button with hover effects"""
        if bg_color is None:
            bg_color = COLORS['bg_light']
        
        btn = tk.Button(parent, text=text, command=command,
                       bg=bg_color, fg=COLORS['text'],
                       font=('Segoe UI', 9, 'bold'),
                       relief='flat',
                       padx=20, pady=8,
                       cursor='hand2',
                       borderwidth=0)
        
        # Hover effects
        def on_enter(e):
            btn['bg'] = COLORS['accent_hover']
        
        def on_leave(e):
            btn['bg'] = bg_color
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

    def create_modern_entry(self, parent):
        """Create a modern styled entry with aqua/green accent"""
        entry = tk.Entry(parent,
                        bg=COLORS['input_bg'],
                        fg=COLORS['text'],
                        insertbackground=COLORS['accent'],
                        font=('Segoe UI', 10),
                        relief='flat',
                        borderwidth=2,
                        highlightthickness=2,
                        highlightbackground=COLORS['border'],
                        highlightcolor=COLORS['success'])
        
        return entry

    def setup_ui(self):
        # === Header ===
        header = tk.Frame(self.root, bg=COLORS['bg_dark'], height=60)
        header.pack(fill="x", padx=20, pady=(10, 0))
        
        title = tk.Label(header, text="🌿 SEED MANAGER", 
                        font=('Segoe UI', 24, 'bold'),
                        bg=COLORS['bg_dark'], 
                        fg=COLORS['accent'])
        title.pack(side='left', pady=10)
        
        subtitle = tk.Label(header, text="Organize • Track • Grow", 
                           font=('Segoe UI', 10),
                           bg=COLORS['bg_dark'], 
                           fg=COLORS['text_dim'])
        subtitle.pack(side='left', padx=20, pady=10)

        # === Toolbar ===
        toolbar = tk.Frame(self.root, bg=COLORS['bg_medium'], height=50)
        toolbar.pack(fill="x", padx=20, pady=10)
        
        # Left side buttons
        left_frame = tk.Frame(toolbar, bg=COLORS['bg_medium'])
        left_frame.pack(side='left', pady=10, padx=10)
        
        self.create_modern_button(left_frame, "↑ Sort by Name", self.sort_by_name).pack(side="left", padx=3)
        self.create_modern_button(left_frame, "↑ Sort by Type", self.sort_by_type).pack(side="left", padx=3)
        self.create_modern_button(left_frame, "✓ Heirloom Only", self.filter_heirloom, COLORS['success']).pack(side="left", padx=3)
        
        # Right side filters
        right_frame = tk.Frame(toolbar, bg=COLORS['bg_medium'])
        right_frame.pack(side='right', pady=10, padx=10)
        
        # Pairing Filter
        tk.Label(right_frame, text="PAIRING:", bg=COLORS['bg_medium'], 
                fg=COLORS['text_dim'], font=('Segoe UI', 8, 'bold')).pack(side="left", padx=(10, 5))
        pairings = sorted(set(row.get("Pairings", "") for row in self.data if row.get("Pairings", "")))
        self.pairing_var = tk.StringVar()
        self.pairing_dropdown = ttk.Combobox(right_frame, textvariable=self.pairing_var, 
                                            values=pairings, width=15, font=('Segoe UI', 9))
        self.pairing_dropdown.pack(side="left", padx=5)
        self.pairing_dropdown.bind("<<ComboboxSelected>>", self.filter_pairing)
        
        # Season Filter
        tk.Label(right_frame, text="SEASON:", bg=COLORS['bg_medium'], 
                fg=COLORS['text_dim'], font=('Segoe UI', 8, 'bold')).pack(side="left", padx=(10, 5))
        seasons = sorted(set(row.get("Season/s", "") for row in self.data if row.get("Season/s", "")))
        self.season_var = tk.StringVar()
        self.season_dropdown = ttk.Combobox(right_frame, textvariable=self.season_var, 
                                           values=seasons, width=15, font=('Segoe UI', 9))
        self.season_dropdown.pack(side="left", padx=5)
        self.season_dropdown.bind("<<ComboboxSelected>>", self.filter_season)
        
        self.create_modern_button(right_frame, "⟲ Reset", self.reset_filters).pack(side="left", padx=5)

        # === Table Container ===
        table_container = tk.Frame(self.root, bg=COLORS['bg_dark'])
        table_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        table_frame = tk.Frame(table_container, bg=COLORS['border'], padx=1, pady=1)
        table_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, columns=COLUMNS, show="headings", height=15)

        for col in COLUMNS:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=150, anchor="w")

        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbars
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        y_scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=y_scroll.set)

        x_scroll = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        x_scroll.pack(fill="x")
        self.tree.configure(xscrollcommand=x_scroll.set)

        self.tree.bind("<Double-1>", self.load_selected_to_form)

        self.refresh_table()

        # === Form Section ===
        form_container = tk.Frame(self.root, bg=COLORS['bg_dark'])
        form_container.pack(fill="x", padx=20, pady=(0, 20))
        
        form_frame = tk.LabelFrame(form_container, 
                                   text=" ADD / EDIT SEED ",
                                   bg=COLORS['bg_medium'], 
                                   fg=COLORS['accent'],
                                   font=('Segoe UI', 11, 'bold'),
                                   borderwidth=2,
                                   relief='flat',
                                   padx=15, 
                                   pady=15)
        form_frame.pack(fill="x")

        # Create grid layout for fields - 4 columns
        self.entries = {}
        fields_to_show = COLUMNS[:8]
        
        for i, col in enumerate(fields_to_show):
            row = i // 4
            column = (i % 4) * 2
            
            label = tk.Label(form_frame, text=col.upper(), 
                           bg=COLORS['bg_medium'], 
                           fg=COLORS['text_dim'],
                           font=('Segoe UI', 8, 'bold'))
            label.grid(row=row, column=column, sticky="w", padx=(5, 5), pady=8)
            
            entry = self.create_modern_entry(form_frame)
            entry.grid(row=row, column=column+1, sticky="ew", padx=(0, 15), pady=8)
            self.entries[col] = entry
        
        # Make columns expand proportionally
        for i in range(8):
            form_frame.columnconfigure(i, weight=1 if i % 2 == 1 else 0)

        # === Action Buttons ===
        button_frame = tk.Frame(form_container, bg=COLORS['bg_dark'])
        button_frame.pack(pady=(15, 0))
        
        self.create_modern_button(button_frame, "➕ ADD / UPDATE", 
                                 self.add_or_update_entry, COLORS['success']).pack(side="left", padx=5)
        self.create_modern_button(button_frame, "🗑 DELETE", 
                                 self.delete_entry, '#ef4444').pack(side="left", padx=5)
        self.create_modern_button(button_frame, "✖ CLEAR FORM", 
                                 self.clear_form).pack(side="left", padx=5)
        self.create_modern_button(button_frame, "💾 EXPORT CSV", 
                                 self.export_csv, COLORS['accent']).pack(side="left", padx=5)

    # === Toolbar Functions ===
    def sort_by_name(self):
        self.filtered_data = sorted(self.filtered_data, key=lambda x: x.get("Name", "").lower())
        self.refresh_table()

    def sort_by_type(self):
        self.filtered_data = sorted(self.filtered_data, key=lambda x: x.get("Type", "").lower())
        self.refresh_table()

    def filter_heirloom(self):
        self.filtered_data = [row for row in self.data if row.get("Heirloom (Y/N)", "").lower() == "y"]
        self.refresh_table()

    def filter_pairing(self, event=None):
        val = self.pairing_var.get().lower()
        self.filtered_data = [row for row in self.data if val in row.get("Pairings", "").lower()]
        self.refresh_table()

    def filter_season(self, event=None):
        val = self.season_var.get().lower()
        self.filtered_data = [row for row in self.data if val in row.get("Season/s", "").lower()]
        self.refresh_table()

    def reset_filters(self):
        self.filtered_data = self.data.copy()
        self.pairing_var.set("")
        self.season_var.set("")
        self.refresh_table()

    def load_selected_to_form(self, event=None):
        """Load selected row into form for editing"""
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        values = self.tree.item(selected_item, "values")
        for i, col in enumerate(COLUMNS[:8]):
            self.entries[col].delete(0, tk.END)
            if i < len(values):
                self.entries[col].insert(0, str(values[i]))

    # === CRUD ===
    def add_or_update_entry(self):
        new_entry = {col: self.entries[col].get() for col in COLUMNS}
        
        for col in COLUMNS:
            if col not in new_entry:
                new_entry[col] = ""

        if not new_entry["Name"]:
            messagebox.showwarning("Input Error", "Name field cannot be empty.")
            return

        found = False
        for i, row in enumerate(self.data):
            if row.get("Name", "") == new_entry["Name"]:
                self.data[i] = new_entry
                found = True
                break
        
        if not found:
            self.data.append(new_entry)

        self.save_to_csv()
        self.reset_filters()
        self.refresh_table()

        messagebox.showinfo("Success", f"Entry for '{new_entry['Name']}' added/updated successfully.")
        self.clear_form()

    def delete_entry(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Select a row", "Please select a row to delete.")
            return

        name = self.tree.item(selected_item, "values")[0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?"):
            self.data = [row for row in self.data if row.get("Name", "") != name]
            self.save_to_csv()
            self.reset_filters()
            self.refresh_table()
            messagebox.showinfo("Deleted", f"Entry for '{name}' deleted successfully.")

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=COLUMNS)
                writer.writeheader()
                writer.writerows(self.data)
            messagebox.showinfo("Exported", f"Data exported successfully to {file_path}")

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for row in self.filtered_data:
            values = [row.get(col, "") for col in COLUMNS]
            self.tree.insert("", "end", values=values)

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)


def main():
    root = tk.Tk()
    app = SeedManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
