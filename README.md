# 🌱 Seed Manager

A sleek and modern **Seed Management Tool** built with **Python** and **Tkinter**. Easily track your seeds, germination times, planting schedules, and more—all stored in an **Excel file**. Perfect for gardeners, hobbyists, and small farms.

---

## Snapshot

![Seed Manager Snapshot](snapshot.png)

---

## Features

- **Efficient Management:** Clear form and table view for managing seeds.
- **Auto-Save:** Ensures all data is automatically saved to prevent loss.
- **Multi-Value Fields:** Supports complex seed information with fields like spacing or depth allowing multiple entries.
- **Intuitive Input:** Includes date and temperature pickers for easy data entry.
- **Filter and Edit:** Easily find and modify seeds via a dropdown menu or direct table selection.
- **Data Integrity:** Options to clear the form or delete a selected row.
- **Portable Data:** Saves all information to a standard **Excel file** (`.xlsx`) for portability and backup.

---

## Requirements

This app requires **Python 3.10+** and the following packages:
pandas==2.3.3
openpyxl==3.1.5
numpy==2.3.3
python-dateutil==2.9.0.post0
pytz==2025.2
tzdata==2025.2
six==1.17.0
packaging==25.0
et_xmlfile==2.0.0
Install dependencies with:
## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

git clone [https://github.com/VWithun/Garden_Seeds_Manager/tree/main](https://github.com/VWithun/Garden_Seeds_Manager/tree/main)
cd Seed-Manager

2. Ensure the Excel file exists
The app expects a default Excel file named seed_list.xlsx with the following columns:


Name, Type, Life Cycle, Germination (days),
Seed Spacing (inches), Temperature (F), Seed Depth (inches),
Approximate Start Date (mm/yy), Transplant Timeframe (weeks),
Time to Maturity (days), Heirloom (Y/N), Season/s,
Benefits, Uses, Pairings, Seed Started Date,
Location, Transplant Date, Harvest Date, Issues, Comments
Note: If the file doesn’t exist, the app will automatically create a blank one with these columns.

3. Run the app
Bash

python seed_manager.py

### How to Use
Add a New Seed

Fill out the form on the left.

Multi-value fields (like spacing and depth) allow multiple entries.

Click Clear Form to reset the input fields.

### Edit a Seed

Select a seed from the dropdown menu or directly in the table.

Modify the necessary fields. The app auto-saves the changes.

### Delete a Seed

Select a seed in the table view.

Click Delete Selected Row.

### Save & Export

Changes are auto-saved to seed_list.xlsx.

Use the Save As function to export a copy of your data to a new file.

### View & Filter

The table view on the right displays all seeds.

Use scrollbars for easy navigation.

### License

This repository is released under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0) license.

You may view the full license here: CC BY-NC-ND 4.0

© 2025 Vanessa W. All rights reserved.
You may not copy, redistribute, or modify this project without explicit permission.
