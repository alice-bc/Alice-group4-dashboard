# World Happiness Dashboard

An interactive Streamlit dashboard exploring how happiness scores have changed over time (2015–2024), built as part of our World Happiness Report project.

---

## What It Does

- Displays the **global average happiness score** by default (2015–2024)
- Filter by **geographic group** and/or **country** in the sidebar to compare specific regions or countries
- Selecting a filter switches the view from the global average to the selected lines only
- Adjust the **year range** with the slider in the main area
- Summary cards at the bottom update automatically based on the current filter state

---

## Project Structure

```
📦 project/
├── happiness_dashboard.py           # Streamlit dashboard (this file)
├── happiness_report_standardized.csv  # Cleaned dataset (from cleaning notebook)
├── requirements.txt
└── README.md
```

---

## Setup & Run

**1. Clone the repo and navigate to the project folder**

```bash
git clone <repo-url>
cd <project-folder>
```

**2. (Optional) Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Make sure the dataset is in the same folder as the dashboard**

```
happiness_report_standardized.csv   ← output from 1_world_happiness_cleaning.ipynb
happiness_dashboard.py
```

**5. Run the dashboard**

```bash
streamlit run happiness_dashboard.py
```

The dashboard will open automatically at `http://localhost:8501`.

---

## Dataset

- **Source:** [World Happiness Report](https://worldhappiness.report/) (Gallup World Poll, 2015–2024)
- **Cleaned by:** `1_world_happiness_cleaning.ipynb`
- **Key columns used:**
  - `Happiness score` — Cantril Ladder score (0–10)
  - `Geographic_Group` — continent-level grouping (added during EDA)
  - `Country_Standardized` — ISO-standardized country names
  - `Year`

---

## Dependencies

| Package | Version |
|---|---|
| streamlit | ≥ 1.58.0 |
| altair | ≥ 6.2.2 |
| pandas | ≥ 2.0.0 |
