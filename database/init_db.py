
#Optional seeding script for initializing DB with default status and categories
# Don't run if using migrations 
import os
import sys

# Ensure project root is on sys.path when running as a script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app, db
from app.models import TicketStatus, Category

DEFAULT_STATUSES = [
    ('Pending', 'Ticket submitted but not yet assigned'),
    ('In Progress', 'Ticket assigned and being worked on'),
    ('Resolved', 'Ticket has been completed'),
    ('Closed', 'Ticket is finalized'),
]

DEFAULT_CATEGORIES = [
    ('IT Support', 'Computer, network, and software issues'),
    ('Facilities', 'Building maintenance, repairs, and cleaning'),
    ('Electrical', 'Power outlets, lighting, electrical systems'),
    ('Plumbing', 'Leaks, clogs, water-related issues'),
    ('HVAC', 'Heating, ventilation, and air conditioning'),
]

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        if TicketStatus.query.count() == 0:
            for name, desc in DEFAULT_STATUSES:
                db.session.add(TicketStatus(status_name=name, description=desc))
        if Category.query.count() == 0:
            for name, desc in DEFAULT_CATEGORIES:
                db.session.add(Category(category_name=name, description=desc))
        db.session.commit()
        print('Database initialized and seeded.')
