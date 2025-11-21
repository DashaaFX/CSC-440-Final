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