from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..forms import TicketForm
from ..models import Ticket, Category, TicketStatus, Role, Comment, Rating
from .. import db

tickets_bp = Blueprint('tickets', __name__, url_prefix='/tickets')

@tickets_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_ticket():
    form = TicketForm()
    # populate categories
    form.category_id.choices = [(c.category_id, c.category_name) for c in Category.query.all()]
    if form.validate_on_submit():
        # validate category exists
        category = Category.query.get(form.category_id.data)
        if not category:
            flash('Please select a valid category.', 'warning')
            return render_template('tickets/new.html', form=form)
        ticket = Ticket(
            title=form.title.data,
            description=form.description.data,
            location=form.location.data,
            category_id=form.category_id.data,
            requester_id=current_user.user_id,
            status_id=TicketStatus.query.filter_by(status_name='Pending').first().status_id
        )
        db.session.add(ticket)
        db.session.commit()
        flash('Ticket submitted.', 'success')
        return redirect(url_for('tickets.my_tickets'))
    return render_template('tickets/new.html', form=form)

@tickets_bp.route('/mine')
@login_required
def my_tickets():
    tickets = Ticket.query.filter_by(requester_id=current_user.user_id).order_by(Ticket.created_at.desc()).all()
    return render_template('tickets/my_tickets.html', tickets=tickets)

@tickets_bp.route('/<int:ticket_id>')
@login_required
def ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    # Access: requester of ticket, assigned technician, or manager can view
    if ticket.requester_id != current_user.user_id and ticket.technician_id != current_user.user_id and getattr(current_user.role, 'value', str(current_user.role)) != 'manager':
        flash('You are not authorized to view this ticket.', 'danger')
        return redirect(url_for('index'))
    comments = Comment.query.filter_by(ticket_id=ticket_id).order_by(Comment.created_at.asc()).all()
    existing_rating = Rating.query.filter_by(ticket_id=ticket_id).first()
    return render_template('tickets/detail.html', ticket=ticket, comments=comments, rating=existing_rating)
