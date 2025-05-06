# Project: Interactive Job Report

**Interactive dashboard to explore scraped job offers and filter them by your skills.**

---

## 🚀 Overview

This project consists of two main parts:

1. **Data scraper** using Playwright + Python to collect job postings from the JustJoinIt site, save them into a CSV file (`justjoinit_offers.csv`).
2. **Interactive dashboard** built with Dash and Bootstrap for:

   * Displaying your selected skills as clickable badges
   * Filtering job offers by skill match score
   * Sorting results by relevance

## 📁 Repository Structure

```
Web Scrapping/
├── assets/
│   └── custom.css         # Custom dark‐mode styles for Dash
├── app.py                 # Main Dash application
├── justjoinit_offers.csv  # Scraped job data (sample)
├── scraper_justjoinit.py  # Playwright scraper script
├── README.md              # Project documentation
└── .gitignore
```

## 🛠️ Installation & Setup

1. **Clone the repo**

   ```bash
   git clone https://github.com/rjgrajewski/it_job_offers
   cd it_job_offers
   ```

2. **Create virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\\Scripts\\activate  # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the scraper**

   ```bash
   python scraper_justjoinit.py
   ```

   This generates or updates `justjoinit_offers.csv`.

5. **Start the dashboard**

   ```bash
   python app.py
   ```

   Open `http://127.0.0.1:8050` in your browser.

## ⚙️ Configuration

* **CSV\_PATH** in `app.py` points to `justjoinit_offers.csv`.
* **assets/custom.css**: overrides Dash theme for full dark mode, custom badges, and layout tweaks.

  * Height of `#react-entry-point` and sidebar forced to 100vh for full‐height layout.

## 📑 Code Highlights

### `scraper_justjoinit.py`

* Uses Playwright sync API to scroll and collect all job‐offer URLs.
* Visits each link, extracts fields (title, category, company, location, salary, tech stack).
* Saves results to CSV.

### `app.py`

* **Dash setup** with `dbc.themes.DARKLY` + `assets/custom.css`.
* \`\` to hold `selected-skills` in session state.
* **Callbacks**:

  * \`\`: adds/removes skills from the store when user interacts (dropdown or badge click).
  * \`\`: re-renders badges and filters/sorts the DataTable by `match_score`.
* \`\` computes relevance:

  ```python
  cnt = len(set(selected) & set(row_skills))
  return cnt + round(cnt/len(row_skills), 2)
  ```

## 📂 Assets & Styling

* Custom CSS in `assets/custom.css`:

  * Sets dark‐mode background and text colors globally.
  * Styles badges, dropdowns, DataTable for readability.
  * Forces full‐height sidebar and main content (`100vh`).

## 📝 Future Improvements

* Enhance **skill suggestions** with live search and fuzzy matching.
* Deploy to Heroku or similar, include Dockerfile.