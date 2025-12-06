# Campus Work Order System

A web application allowing students to submit work orders for any matters
requiring attention on campus. Students may submit requests, and faculty and
admins may modify and manage requests.

## Technology Stack

- Python 3 + Flask for web framework
- Plain HTML templates with Jinja2
- Custom CSS for styling

## Setup (Windows CMD)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
mkdir instance
set FLASK_APP=app.py
flask db upgrade
python app.py
```

## Setup (macOS)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir -p instance
export FLASK_APP=app.py
flask db upgrade
python3 app.py
```

The app will run on http://localhost:5001

## Current Features

- Authentication and registration (requester by default)
- Role-based dashboards: requester, technician, manager
- Ticket submission (requester), technician status updates, manager 		assignment
- Search & filtering: keyword, category, status, date range, sort (requester & manager)
- CSV export of tickets (manager), with report logging
- Comments on tickets (requester/technician), requester rating after resolution

## Database Schema

- Managed with Flask-Migrate from SQLAlchemy models
- Default database: SQLite file `instance/ticket_system.db`
- Optional: MySQL via `DATABASE_URL` (see `.env.example`)
- See `database_docs/schema.sql` for raw SQL structure

### Main Tables
- `users` — Accounts, password hash, role (requester/technician/manager)
- `categories` — Ticket categories (IT Support, Facilities, etc.)
- `ticket_status` — Workflow states (Pending, In Progress, Resolved, Closed)
- `tickets` — Title, description, location, category/status, requester/technician, timestamps
- `comments` — Per-ticket comments linked to users
- `ratings` — Requester rating and feedback (one per ticket)
- `report_logs` — Manager report generation audit entries

## Database Options
Default: SQLite (`sqlite:///instance/ticket_system.db`) if `DATABASE_URL` not set.
MySQL: set `DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/dbname` in `.env`.
Do NOT mix running raw `schema.sql` and migrations on the same fresh DB. Choose one initialization path.

## Migrations Workflow (Flask-Migrate)
```cmd
set FLASK_APP=app.py
flask db migrate -m "describe change"
flask db upgrade
```
If you imported an existing schema manually, align with: `flask db stamp head` before first migrate.

### Optional: Seed Defaults via Script
If you want to ensure default statuses/categories outside migrations:
```cmd
set FLASK_APP=app.py
python database\init_db.py
```


## Additional Notes (for teammates)

- Env: copy `.env.example` → `.env` and set your MySQL creds (`DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/dbname`).
- Driver: install MySQL driver `pymysql` if missing.
- DB init: run either `database/schema.sql` (creates + seeds) OR `flask db upgrade` (migrations). Do not run both.
- Seed: ensure statuses/categories exist (from schema.sql or a seed step) to avoid empty dropdowns.


## Project Structure
```
app/            core application
	dashboard/    role-based dashboards & routes
	tickets/      ticket creation & detail
	comments/     commenting features
	ratings/      requester ratings on resolved tickets
	reports/      (future/placeholder reporting)
	templates/    Jinja2 HTML templates
	static/       CSS assets
database/       schema.sql and optional seed script
migrations/     Alembic migration versions
```

## CSV Export
Manager dashboard button triggers `/dashboard/manager/export.csv` applying current filters and logging a `report_logs` row.

## Environment Variables
`SECRET_KEY` (session security) , `DATABASE_URL` (override default DB).


## Troubleshooting
- Missing table error: run `flask db upgrade`.
- Stuck on SQLite: set `DATABASE_URL` then re-run migrate/upgrade on new DB.
- Status change blocked: technicians cannot skip or go backward.

