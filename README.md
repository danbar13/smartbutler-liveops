# 🛎️ SmartButler® LiveOps Digest — Operational Morning Briefing & SLA Tracking

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**SmartButler® LiveOps Digest** is an executive-grade operational briefing and SLA analytics platform built for luxury hotels and hospitality resorts running **SmartButler®** systems (by [JAYBEE Systems Ltd.](https://www.jaybee.com)).

The system ingests raw daily operational log reports (PDF, CSV, JSON), parses departments and guest service requests, clusters recurring issues and cross-departmental bottlenecks, and generates actionable morning briefings for hotel management and department heads.

---

## ✨ Key Features

- **🌐 Dual-Language Support (Bilingual Hebrew / English):**
  - Instant one-click toggle in the header and sidebar with national flag indicators.
  - Native Right-to-Left (RTL) for Hebrew and Left-to-Right (LTR) for English.
  - Full translations for all departments, ticket categories, table headers, and executive action directives.

- **📱 Fully Responsive Mobile-First Design:**
  - Executive 2×2 metric KPI dashboard optimized for smartphones.
  - Horizontal touch-scrollable tabs and data tables with sticky headers.
  - High-contrast, clean UI compatible with both Dark Mode and Light Mode.

- **📋 4-Tab Executive Workflow:**
  1. **📤 Ingestion & Archive (העלאת דוחות ושמירה):** Upload PDF / CSV / JSON reports, auto-save to historical SQLite database, and switch between previous dates.
  2. **📋 Executive Standup Briefing (תדריך להנהלה - ישיבת בוקר):** Daily executive summary, active departments, SLA adherence rate, total labor hours, and departmental breakdown table.
  3. **🔍 Deep Insights & SLA Bottlenecks (תובנות עיקריות ומשמעותיות):**
     - Problematic rooms under special focus (cross-departmental ticket concentration).
     - Recurring issues per room / floor cluster (e.g. chronic A/C leaks, towel shortages).
     - Service category frequency and SLA achievement.
     - Extended duration tracking (extreme SLA breach ratios).
     - Staff member SLA compliance monitoring.
  4. **📊 Department Modules & Actionable Directives (פירוט לפי מודולים ומחלקות):** Filter by Housekeeping, Engineering, Front Desk, F&B, with auto-generated departmental directives.

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/danbar13/smartbutler-liveops.git
cd smartbutler-liveops
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📁 Project Structure

```text
├── app.py                      # Main Streamlit application and responsive layout
├── i18n.py                     # Bilingual internationalization dictionary & briefing generator
├── engine.py                   # Analytics engine (SLA calculations, clustering, anomalies)
├── db.py                       # SQLite database manager for report persistence
├── parsers/                    # Report parsing engine (PDF, CSV, JSON)
│   ├── pdf_parser.py           # Robust tabular PDF parsing (pdfplumber)
│   ├── csv_parser.py           # Structured CSV ingestion
│   ├── json_parser.py          # Native JSON log importer
│   └── models.py               # Data transfer models
├── data/                       # Local SQLite database & uploads storage
├── assets/                     # Branding logos and graphics
├── reports/                    # Exported briefings and digests
└── requirements.txt            # Python package dependencies
```

---

## 🛠️ Tech Stack

- **Frontend & App Framework:** [Streamlit](https://streamlit.io/)
- **Data Analysis & Processing:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Document & PDF Parsing:** [pdfplumber](https://github.com/jsvine/pdfplumber), [pypdf](https://pypdf.readthedocs.io/)
- **Database:** SQLite3
- **Styling:** Custom CSS3 with dynamic RTL/LTR injection, CSS Grid, and Media Queries

---

## 🏢 About

Developed for **JAYBEE Systems Ltd.** ([www.jaybee.com](https://www.jaybee.com)), creators of the **SmartButler®** hotel operations platform.
