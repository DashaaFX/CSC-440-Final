from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from ..forms import RegistrationForm, LoginForm
from ..models import User, Role
from .. import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower()).first()
        if existing:
            flash('Email already registered.', 'warning')
            return redirect(url_for('auth.register'))
        user = User(
            email=form.email.data.lower(),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=Role(form.role.data)
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if not user or not user.check_password(form.password.data):
            flash('Invalid credentials.', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user)
        flash('Logged in successfully.', 'success')
        # Role-based default redirect if no explicit 'next'
        next_url = request.args.get('next')
        if not next_url:
            if user.role.value == 'requester':
                next_url = url_for('dashboard.requester_dashboard')
            elif user.role.value == 'technician':
                next_url = url_for('dashboard.technician_dashboard')
            elif user.role.value == 'manager':
                next_url = url_for('dashboard.manager_dashboard')
            else:
                next_url = url_for('index')
        return redirect(next_url)
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('index'))
