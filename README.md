# Campus Helpdesk

Campus Helpdesk is a Flask web application for students to report campus issues and for Heads of Department (HODs) to review and manage them.

## Features

- Student registration and login
- Issue submission with category, priority, and optional image/PDF attachment
- Private issue tracking and discussion
- Optional public issue board with upvotes
- HOD dashboard with issue counts, search, filters, and pagination
- HOD issue status updates and replies
- Responsive interface with a light/dark theme toggle

## Requirements

- Python 3.9 or newer
- pip

## Run locally

From the project directory, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux, activate it with:

```bash
source .venv/bin/activate
```

Install the dependencies and start the development server:

```bash
python -m pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. The app creates its SQLite database and upload directory as needed.

## Configuration

Set `FLASK_SECRET_KEY` to a long, random value for a stable session key, especially before deploying:

```powershell
$env:FLASK_SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
```

The app generates a temporary key when this variable is not set, so existing sessions will be invalidated when the process restarts. Do not use the built-in Flask development server for production.

Attachments are limited to 16 MB and accept PNG, JPG, JPEG, and PDF files.

## Demo accounts

`python create_accounts.py` creates sample student and HOD accounts for local testing. **It drops and recreates all database tables**, so only run it against a disposable local database. The script prints the demo login details after creating them. Do not use its sample credentials in a deployed environment.

## Project structure

```text
app.py                 Flask application, routes, and database models
create_accounts.py     Local demo-data setup script
init_db.py             SQLite schema initialization script
requirements.txt       Python dependencies
static/style.css       Application styles
templates/             Jinja templates for the application pages
```
