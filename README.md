# Smart Food Saver

A Streamlit app for tracking food inventory, planning meals, generating AI recipe suggestions, and monitoring food waste.

## Requirements

- Python 3.10 or later
- A Gemini API key for AI recipe suggestions

## Setup

From the project directory, create and activate a virtual environment, then install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set `GEMINI_API_KEY` to your own key. Keep `.env` private; it is excluded from Git.

## Run

```powershell
streamlit run app.py
```

The SQLite database is created locally as `food_saver.db` when the app starts. It is not included in Git.
