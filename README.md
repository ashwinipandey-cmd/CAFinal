# CA Final Tracker

A Streamlit-based study planner and progress dashboard for CA Final preparation. The app tracks hours, syllabus coverage, and target completion across subjects with a modern visual UI.

## Features

- Subject-wise planning for:
  - FR (Financial Reporting)
  - AFM (Advanced Financial Management & Economics)
  - AA (Advanced Auditing)
  - DT (Direct Tax & International Tax)
  - IDT (Indirect Tax)
- Topic-level tracking with predefined syllabus buckets.
- Progress analytics and visual charts powered by Plotly.
- Supabase-backed persistence for study logs and app data.
- Streamlit UI with custom neon/glass theme.

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
- Supabase (Python client)

## Project Structure

- `streamlit_app.py` — Main Streamlit application.
- `requirements.txt` — Python dependencies.
- `CA_Final_Tracker.xlsx` — Local tracker spreadsheet reference.

## Prerequisites

- Python 3.10+
- pip
- Supabase project with credentials

## Installation

1. Clone the repository:

   ```bash
   git clone <your-repo-url>
   cd CAFinal
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

This app reads Supabase credentials from Streamlit secrets.

Create `.streamlit/secrets.toml` with:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-or-service-key"
```

> Keep credentials private and never commit secrets to version control.

## Running the App

```bash
streamlit run streamlit_app.py
```

Then open the local URL shown in the terminal (usually `http://localhost:8501`).

## Notes

- Default exam date in code is set to `2027-01-01`.
- The app stops execution if Supabase connection fails.

## License

Add your preferred license details here.
