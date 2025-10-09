# 🌱 **Seed Manager**

> A sleek, modern, and intuitive **Seed Management Tool** built with **Python + Tkinter**.  
Easily track your seeds, germination times, planting schedules, and more—all stored securely in an Excel file.  
Perfect for **gardeners**, **hobbyists**, and **small farms** 🌾

---

## 📸 **Snapshot**
![Seed Manager Screenshot](https://github.com/VWithun/Garden_Seeds_Manager/blob/main/image.png)  
<sub>*Modern, dark-mode inspired interface with smooth interactions and real-time data updates.*</sub>

---

## ✨ **Features**

- 🪴 **Efficient Management:** Clean form + interactive table for seed tracking.  
- 💾 **Auto-Save:** Never lose your progress — all edits are saved automatically.  
- 🌿 **Multi-Value Fields:** Add complex details like spacing or depth with multi-entry support.  
- 🗓️ **Intuitive Input:** Built-in date and temperature pickers for seamless data entry.  
- 🔍 **Filter & Edit:** Quickly find and update any seed using dropdowns or table clicks.  
- 🧹 **Data Integrity Tools:** One-click “Clear Form” and “Delete Row” options.  
- 📤 **Portable Data:** Save and share your garden database via standard Excel files (`.xlsx`).  
- 🌗 **Dark Mode Inspired:** A modern interface for comfortable viewing.

---

## ⚙️ **Requirements**

Ensure you have **Python 3.10+** installed.  
Then install dependencies with:

```bash
pip install -r requirements.txt
Required packages:

ini
Copy code
pandas==2.3.3
openpyxl==3.1.5
numpy==2.3.3
python-dateutil==2.9.0.post0
pytz==2025.2
tzdata==2025.2
six==1.17.0
packaging==25.0
et_xmlfile==2.0.0

🚀 Getting Started
1️⃣ Clone the Repository
bash
Copy code
git clone https://github.com/VWithun/Garden_Seeds_Manager.git
cd Seed-Manager
2️⃣ Ensure Excel File Exists
The app expects a file named seed_list.xlsx with the following columns:

pgsql
Copy code
Name, Type, Life Cycle, Germination (days), Seed Spacing (inches),
Temperature (F), Seed Depth (inches), Approximate Start Date (mm/yy),
Transplant Timeframe (weeks), Time to Maturity (days), Heirloom (Y/N),
Season/s, Benefits, Uses, Pairings, Seed Started Date, Location,
Transplant Date, Harvest Date, Issues, Comments
🧩 If the file doesn’t exist, the app will automatically create a blank version with these columns.

▶️ Run the App
bash
Copy code
python seed_manager.py
🌼 How to Use
➕ Add a New Seed
Fill out the form on the left.

Fields like Spacing or Depth can accept multiple values.

Click Clear Form to reset all inputs.

✏️ Edit a Seed
Select a seed from the dropdown or table.

Make your edits — changes save automatically.

❌ Delete a Seed
Select a seed in the table view.

Click Delete Selected Row.

💾 Save & Export
All changes are auto-saved to seed_list.xlsx.

Use Save As to export a copy to a new file.

🔎 View & Filter
Scroll through your full seed list in the table view.

Use built-in scrollbars for smooth navigation.

🧠 Tech Stack
Technology	Purpose
Python	Core programming language
Tkinter	GUI framework
Pandas	Data management
OpenPyXL	Excel integration
NumPy	Data manipulation
Dark Theme	Sleek and comfortable interface

📄 License
This repository is released under the
Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0) license.

You may read the full license here:
👉 CC BY-NC-ND 4.0 License

© 2025 VWithun -- https://github.com/VWithun/
All rights reserved. You may not copy, redistribute, or modify this project without explicit permission.

