# Certification_Tracker
# 👨‍💻 IT Certification & Fee Tracker

A powerful, local web application built with **Streamlit** and **Pandas** to help IT professionals manage their active certifications, track expiration dates, calculate annual maintenance fees (AMFs), and prioritize renewals.

<img width="1869" height="763" alt="image" src="https://github.com/user-attachments/assets/c118499c-9915-4da0-8718-26f7e8eefe41" />

## ✨ Features

* **Persistent Storage:** All certification data is stored locally in a single **`certifications.json`** file.
* **Guaranteed Sorting:** Provides a **"Sort Table By:"** selector to reliably order the main certification list by Expiration Date, Date Achieved, Name, or Fee, ensuring the table always appears as you need it.
* **AMF Calculation:** Automatically estimates the total annual cost for maintaining all recurring certifications (Annual, Biennial, Triennial fees).
* **Urgency Block:** A dedicated **"Certifications Due Soon"** section that filters and displays certifications expiring within the next **180 days**, prioritized by days left until expiration.
* **Data Entry:** Easily add new certifications via a dedicated, structured input form.

---

## 🚀 Quick Start

Follow these steps to get your Certification Tracker running on your local machine.

### Prerequisites

You need **Python 3.8+** installed.

### 1. Installation

Open your terminal or command prompt and run:

```bash
# Install the required Python libraries
pip install streamlit pandas
```

### 2. Prepare the Code
Create a file named streamlit_app.py and paste the entire Python code block provided in the Usage Guide below into it.

### 3. Run the Application
Execute the Python script using Streamlit:
```bash
python3 -m streamlit run streamlit_app.py
```

The application will automatically open in your default web browser (usually at http://localhost:8501).

## 📖 Usage Guide
### Data Management Philosophy
Since standard interactive table sorting can be unstable across different versions of Streamlit, this application uses a robust form-based entry and selector-based sorting model for maximum reliability:

- Adding Data: Use the form on the left.
- Sorting Data: Use the "Sort Table By:" selector above the table.
- Editing/Deleting Data: For maintenance, you must manually edit the certifications.json file and then refresh the app.

#### Sorting the Main Table
- The main table's display order is determined by your selection in the dropdown:
- Use the "Sort Table By:" dropdown to choose the column (e.g., Expiration Date, Fee, Name).
- Use the "Sort Ascending" checkbox to toggle the direction of the sort.
- The entire table will reorder based on your selection.

ENJOY!
