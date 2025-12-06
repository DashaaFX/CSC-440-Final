from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import Ticket, TicketStatus, User, Role
from ..utils import role_required, is_requester, is_technician, is_manager, paginate
from .. import db

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/requester')
@login_required
@role_required(Role.requester)
def requester_dashboard():
    status_filter = request.args.get('status')
    keyword = request.args.get('q', type=str)
    category_id = request.args.get('category_id', type=int)
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    sort = request.args.get('sort', default='created_desc')

    page = request.args.get('page', type=int, default=1)
    per_page = 10

    q = Ticket.query.filter_by(requester_id=current_user.user_id)

    if status_filter:
        status = TicketStatus.query.filter_by(status_name=status_filter).first()
        if status:
            q = q.filter(Ticket.status_id == status.status_id)

    if keyword:
        like = f"%{keyword}%"
        q = q.filter((Ticket.title.ilike(like)) | (Ticket.description.ilike(like)))

    if category_id:
        q = q.filter(Ticket.category_id == category_id)

    if start_date:
        try:
            from datetime import datetime
            sd = datetime.fromisoformat(start_date)
            q = q.filter(Ticket.created_at >= sd)
        except ValueError:
            pass
    if end_date:
        try:
            from datetime import datetime
            ed = datetime.fromisoformat(end_date)
            q = q.filter(Ticket.created_at <= ed)
        except ValueError:
            pass

    if sort == 'created_asc':
        q = q.order_by(Ticket.created_at.asc())
    elif sort == 'status':
        # join status for sorting by name
        q = q.join(TicketStatus, Ticket.status_id == TicketStatus.status_id).order_by(TicketStatus.status_name.asc(), Ticket.created_at.desc())
    elif sort == 'category':
        from ..models import Category
        q = q.join(Category, Ticket.category_id == Category.category_id, isouter=True).order_by(Category.category_name.asc().nulls_last(), Ticket.created_at.desc())
    else:
        q = q.order_by(Ticket.created_at.desc())

    pagination = paginate(q, page, per_page)
    statuses = TicketStatus.query.all()
    from ..models import Category
    categories = Category.query.all()
    return render_template(
        'dashboard/requester.html',
        pagination=pagination,
        tickets=pagination['items'],
        statuses=statuses,
        categories=categories,
        status_filter=status_filter,
        keyword=keyword,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
        sort=sort,
    )

@dashboard_bp.route('/technician')
@login_required
@role_required(Role.technician)
def technician_dashboard():
    # Filters
    status_filter = request.args.get('status')
    keyword = request.args.get('q', type=str)
    category_id = request.args.get('category_id', type=int)

    page = request.args.get('page', type=int, default=1)
    per_page = 10

    q = Ticket.query.filter(Ticket.technician_id == current_user.user_id)

    if status_filter:
        status = TicketStatus.query.filter_by(status_name=status_filter).first()
        if status:
            q = q.filter(Ticket.status_id == status.status_id)

    if category_id:
        q = q.filter(Ticket.category_id == category_id)

    if keyword:
        like = f"%{keyword}%"
        q = q.filter((Ticket.title.ilike(like)) | (Ticket.description.ilike(like)))

    q = q.order_by(Ticket.created_at.desc())

    pagination = paginate(q, page, per_page)
    statuses = TicketStatus.query.order_by(TicketStatus.status_name.asc()).all()
    from ..models import Category
    categories = Category.query.order_by(Category.category_name.asc()).all()
    return render_template('dashboard/technician.html',
                           pagination=pagination,
                           tickets=pagination['items'],
                           statuses=statuses,
                           categories=categories,
                           status=status_filter,
                           category_id=category_id,
                           q=keyword)

@dashboard_bp.route('/technician/<int:ticket_id>/status', methods=['POST'])
@login_required
@role_required(Role.technician)
def technician_update_status(ticket_id):
    new_status = request.form.get('status')
    ticket = Ticket.query.get_or_404(ticket_id)
    # Only assigned technician can update
    if ticket.technician_id != current_user.user_id:
        flash('You can only update your assigned tickets.', 'danger')
        return redirect(url_for('dashboard.technician_dashboard'))
    status = TicketStatus.query.filter_by(status_name=new_status).first()
    if not status:
        flash('Invalid status.', 'warning')
        return redirect(url_for('dashboard.technician_dashboard'))
    # Ensure linear status flow: Pending -> In Progress -> Resolved -> Closed
    order = ['Pending', 'In Progress', 'Resolved', 'Closed']
    current_name = ticket.status.status_name if ticket.status else 'Pending'
    try:
        cur_idx = order.index(current_name)
        new_idx = order.index(status.status_name)
    except ValueError:
        flash('Unsupported status transition.', 'warning')
        return redirect(url_for('dashboard.technician_dashboard'))
    #  Remain at current status or change to next status.
    #  Statuses cannot be skipped or moved backward.
    if new_idx < cur_idx or new_idx > cur_idx + 1:
        flash('Cannot skip steps or move backward. Follow workflow.', 'warning')
        return redirect(url_for('dashboard.technician_dashboard'))
    ticket.status_id = status.status_id
    db.session.commit()
    flash('Status updated.', 'success')
    return redirect(url_for('dashboard.technician_dashboard'))

@dashboard_bp.route('/manager')
@login_required
@role_required(Role.manager)
def manager_dashboard():
    status_filter = request.args.get('status')
    unassigned = request.args.get('unassigned', type=int)
    keyword = request.args.get('q', type=str)
    category_id = request.args.get('category_id', type=int)
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    sort = request.args.get('sort', default='created_desc')
    page = request.args.get('page', type=int, default=1)
    per_page = 10
    q = Ticket.query
    if status_filter:
        status = TicketStatus.query.filter_by(status_name=status_filter).first()
        if status:
            q = q.filter(Ticket.status_id == status.status_id)
    if unassigned:
        q = q.filter(Ticket.technician_id.is_(None))
    if keyword:
        like = f"%{keyword}%"
        q = q.filter((Ticket.title.ilike(like)) | (Ticket.description.ilike(like)))
    if category_id:
        q = q.filter(Ticket.category_id == category_id)
    if start_date:
        try:
            from datetime import datetime
            sd = datetime.fromisoformat(start_date)
            q = q.filter(Ticket.created_at >= sd)
        except ValueError:
            pass
    if end_date:
        try:
            from datetime import datetime
            ed = datetime.fromisoformat(end_date)
            q = q.filter(Ticket.created_at <= ed)
        except ValueError:
            pass
    if sort == 'created_asc':
        q = q.order_by(Ticket.created_at.asc())
    elif sort == 'status':
        q = q.join(TicketStatus, Ticket.status_id == TicketStatus.status_id).order_by(TicketStatus.status_name.asc(), Ticket.created_at.desc())
    elif sort == 'category':
        from ..models import Category
        q = q.join(Category, Ticket.category_id == Category.category_id, isouter=True).order_by(Category.category_name.asc().nulls_last(), Ticket.created_at.desc())
    else:
        q = q.order_by(Ticket.created_at.desc())
    pagination = paginate(q, page, per_page)
    statuses = TicketStatus.query.all()
    technicians = User.query.filter_by(role=Role.technician, is_active=True).all()
    from ..models import Category
    categories = Category.query.all()
    return render_template('dashboard/manager.html', pagination=pagination, tickets=pagination['items'], statuses=statuses, technicians=technicians,
                           categories=categories, status_filter=status_filter, unassigned=unassigned, keyword=keyword,
                           category_id=category_id, start_date=start_date, end_date=end_date, sort=sort)

@dashboard_bp.route('/manager/export.csv')
@login_required
@role_required(Role.manager)
def manager_export_csv():
    # Use current filters 
    status_filter = request.args.get('status')
    unassigned = request.args.get('unassigned', type=int)
    keyword = request.args.get('q', type=str)
    category_id = request.args.get('category_id', type=int)
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    sort = request.args.get('sort', default='created_desc')
    q = Ticket.query
    if status_filter:
        status = TicketStatus.query.filter_by(status_name=status_filter).first()
        if status:
            q = q.filter(Ticket.status_id == status.status_id)
    if unassigned:
        q = q.filter(Ticket.technician_id.is_(None))
    if keyword:
        like = f"%{keyword}%"
        q = q.filter((Ticket.title.ilike(like)) | (Ticket.description.ilike(like)))
    if category_id:
        q = q.filter(Ticket.category_id == category_id)
    if start_date:
        try:
            from datetime import datetime
            sd = datetime.fromisoformat(start_date)
            q = q.filter(Ticket.created_at >= sd)
        except ValueError:
            pass
    if end_date:
        try:
            from datetime import datetime
            ed = datetime.fromisoformat(end_date)
            q = q.filter(Ticket.created_at <= ed)
        except ValueError:
            pass
    if sort == 'created_asc':
        q = q.order_by(Ticket.created_at.asc())
    elif sort == 'status':
        q = q.join(TicketStatus, Ticket.status_id == TicketStatus.status_id).order_by(TicketStatus.status_name.asc(), Ticket.created_at.desc())
    elif sort == 'category':
        from ..models import Category
        q = q.join(Category, Ticket.category_id == Category.category_id, isouter=True).order_by(Category.category_name.asc().nulls_last(), Ticket.created_at.desc())
    else:
        q = q.order_by(Ticket.created_at.desc())

    # Log report
    from ..models import ReportLog
    log = ReportLog(manager_id=current_user.user_id, report_type='csv')
    db.session.add(log)
    db.session.commit()

    # Export as CSV
    import csv
    from io import StringIO
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID','Title','Status','Category','Requester','Technician','Created'])
    rows = q.all()
    for t in rows:
        writer.writerow([
            t.ticket_id,
            t.title,
            t.status.status_name if t.status else '',
            t.category.category_name if t.category else '',
            t.requester.first_name if t.requester else '',
            t.technician.first_name if t.technician else '',
            t.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    from flask import Response
    return Response(si.getvalue(), mimetype='text/csv', headers={
        'Content-Disposition': 'attachment; filename="tickets.csv"'
    })

@dashboard_bp.route('/manager/<int:ticket_id>/assign', methods=['POST'])
@login_required
@role_required(Role.manager)
def manager_assign(ticket_id):
    tech_id = request.form.get('technician_id', type=int)
    ticket = Ticket.query.get_or_404(ticket_id)
    if tech_id:
        ticket.technician_id = tech_id
        in_progress = TicketStatus.query.filter_by(status_name='In Progress').first()
        if in_progress and ticket.status and ticket.status.status_name == 'Pending':
            ticket.status_id = in_progress.status_id
        db.session.commit()
        flash('Technician assigned.', 'success')
    else:
        flash('Select a technician.', 'warning')
    return redirect(url_for('dashboard.manager_dashboard'))
