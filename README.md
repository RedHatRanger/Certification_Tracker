# Certification_Tracker
# 👨‍💻 IT Certification & Fee Tracker

A powerful, local web application built with **Streamlit** and **Pandas** to help IT professionals manage their active certifications, track expiration dates, calculate annual maintenance fees (AMFs), and prioritize renewals.

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
