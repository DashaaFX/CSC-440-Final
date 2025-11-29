from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import Rating, Ticket, TicketStatus
from .. import db

ratings_bp = Blueprint('ratings', __name__, url_prefix='/ratings')

@ratings_bp.route('/add', methods=['POST'])
@login_required
def add_rating():
    ticket_id = request.form.get('ticket_id', type=int)
    value = request.form.get('rating_value', type=int)
    feedback = request.form.get('feedback', type=str)
    if not ticket_id or not value:
        flash('Rating value required.', 'warning')
        return redirect(url_for('index'))
    ticket = Ticket.query.get_or_404(ticket_id)
    # Only requester of ticket can rate, and only if Resolved
    if ticket.requester_id != current_user.user_id:
        flash('Only the requester can rate the ticket.', 'danger')
        return redirect(url_for('tickets.ticket_detail', ticket_id=ticket_id))
    if not ticket.status or ticket.status.status_name != 'Resolved':
        flash('You can rate only resolved tickets.', 'warning')
        return redirect(url_for('tickets.ticket_detail', ticket_id=ticket_id))
    existing = Rating.query.filter_by(ticket_id=ticket_id).first()
    if existing:
        existing.rating_value = value
        existing.feedback = feedback
        flash('Rating updated.', 'success')
    else:
        r = Rating(ticket_id=ticket_id, rating_value=value, feedback=feedback)
        db.session.add(r)
        flash('Thank you for your rating.', 'success')
    db.session.commit()
    return redirect(url_for('tickets.ticket_detail', ticket_id=ticket_id))
