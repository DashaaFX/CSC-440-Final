from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import Comment, Ticket
from .. import db

comments_bp = Blueprint('comments', __name__, url_prefix='/comments')

@comments_bp.route('/add', methods=['POST'])
@login_required
def add_comment():
    ticket_id = request.form.get('ticket_id', type=int)
    text = request.form.get('comment_text', type=str)
    if not ticket_id or not text:
        flash('Comment text required.', 'warning')
        return redirect(url_for('index'))
    ticket = Ticket.query.get_or_404(ticket_id)
    # Allow requester of ticket, assigned technician, or manager
    role = getattr(current_user.role, 'value', str(current_user.role))
    if ticket.requester_id != current_user.user_id and ticket.technician_id != current_user.user_id and role != 'manager':
        flash('Not authorized to comment on this ticket.', 'danger')
        return redirect(url_for('index'))
    c = Comment(ticket_id=ticket_id, user_id=current_user.user_id, comment_text=text)
    db.session.add(c)
    db.session.commit()
    flash('Comment added.', 'success')
    return redirect(url_for('tickets.ticket_detail', ticket_id=ticket_id))
