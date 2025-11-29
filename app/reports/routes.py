from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import func
from ..models import Ticket, User, Role, TicketStatus, Category
from ..utils import role_required, paginate

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
@role_required(Role.manager)
def manager_reports():
    # Pagination params
    tech_page = request.args.get('tech_page', type=int, default=1)
    cat_page = request.args.get('cat_page', type=int, default=1)
    per_page = 10

    # Tickets resolved per technician
    resolved = TicketStatus.query.filter_by(status_name='Resolved').first()
    tickets_per_tech = []
    if resolved:
        tickets_per_tech = (
            Ticket.query
            .with_entities(Ticket.technician_id, func.count(Ticket.ticket_id))
            .filter(Ticket.status_id == resolved.status_id, Ticket.technician_id.isnot(None))
            .group_by(Ticket.technician_id)
            .all()
        )
    tech_map = {u.user_id: f"{u.first_name} {u.last_name}" for u in User.query.filter_by(role=Role.technician).all()}

    # Tickets by category
    tickets_by_category = (
        Ticket.query
        .with_entities(Ticket.category_id, func.count(Ticket.ticket_id))
        .group_by(Ticket.category_id)
        .all()
    )
    cat_map = {c.category_id: c.category_name for c in Category.query.all()}

    # Paginate lists and logic
    def list_paginate(data, page):
        total = len(data)
        pages = (total + per_page - 1) // per_page if total else 1
        if page < 1: page = 1
        if page > pages: page = pages
        start = (page - 1) * per_page
        end = start + per_page
        items = data[start:end]
        return {
            'items': items,
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': pages,
            'has_prev': page > 1,
            'has_next': page < pages
        }

    tickets_per_tech_paginated = list_paginate(tickets_per_tech, tech_page)
    category_paginated = list_paginate(tickets_by_category, cat_page)

    return render_template('reports/manager.html',
                           tickets_per_tech_paginated=tickets_per_tech_paginated,
                           tech_map=tech_map,
                           category_paginated=category_paginated,
                           cat_map=cat_map)
