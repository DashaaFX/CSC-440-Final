# Campus Work Order System

A web application allowing students to submit work orders for any matters
requiring attention on campus. Students may submit requests, and faculty and
admins may modify and manage requests.

## Technology Stack

- Python 3 + Flask for web framework
- Plain HTML templates with Jinja2
- Custom CSS for styling

## Setup

```bash
# create virtual environment
python3 -m venv venv
source venv/bin/activate  # on windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt
```

## Running

```bash
# run development server
python3 app.py
```

The app will run on http://localhost:5001

## Current Features

- Homepage with navigation
- Login and Register links (non-functional placeholders)

## Database Schema

The project uses MySQL with these tables below

### Main Tables:
- `users` - User authentication and roles
- `categories` - Ticket categories (IT, Facilities, etc.)
- `ticket_status` - Ticket workflow status
- `tickets` - Main ticket tracking

### Setup:
1. Database schema is managed through Flask-Migrate
2. See `database_docs/schema.sql` for raw SQL structure
3. Run migrations: `flask db upgrade`

### Default Data:
- Statuses: Pending, In Progress, Resolved, Closed
- Categories: IT Support, Facilities, Electrical, Plumbing, HVAC

## Additional Notes (for teammates)

- Env: copy `.env.example` → `.env` and set your MySQL creds (`DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/dbname`).
- Driver: install MySQL driver `pymysql` if missing.
- DB init: run either `database/schema.sql` (creates + seeds) OR `flask db upgrade` (migrations). Do not run both.
- Seed: ensure statuses/categories exist (from schema.sql or a seed step) to avoid empty dropdowns.

## Feature Summary (Current)
- Authentication & Registration (new users default to requester role)
- Role-based dashboards: requester, technician, manager
- Requester filtering: keyword, category, status, date range, sort options
- Manager tools: view all tickets, filter (same set), assign technicians, CSV export
- Technician workflow: linear status progression (Pending → In Progress → Resolved → Closed)


## Database Options
Default: SQLite (`sqlite:///ticket_system.db`) if `DATABASE_URL` not set.
MySQL: set `DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/dbname` in `.env`.
Do NOT mix running raw `schema.sql` and migrations on the same fresh DB. Choose one initialization path.

## Migrations Workflow (Flask-Migrate)
```cmd
set FLASK_APP=app.py
flask db migrate -m "describe change"
flask db upgrade
```
If you imported an existing schema manually, align with: `flask db stamp head` before first migrate.


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
`SECRET_KEY` (session security) | `DATABASE_URL` (override default DB).

## Quick Start (Windows CMD)
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
set FLASK_APP=app.py
flask db upgrade
python app.py
```

## Troubleshooting
- Missing table error: run `flask db upgrade`.
- Stuck on SQLite: set `DATABASE_URL` then re-run migrate/upgrade on new DB.
- Status change blocked: technicians cannot skip or go backward.

