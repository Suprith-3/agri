from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
import threading
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from models import db
from models.user import User
import secrets
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
bcrypt = Bcrypt()
mail = Mail()

mail = Mail()

def send_async_email(app, msg):
    """Send email in a separate thread to avoid blocking the worker."""
    with app.app_context():
        try:
            mail.send(msg)
            print(f"Async email sent successfully to {msg.recipients}")
        except Exception as e:
            print(f"Async email failed: {str(e)}")

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        state = request.form.get('state')
        district = request.form.get('district')
        farm_size = request.form.get('farm_size')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'danger')
            return redirect(url_for('auth.login'))

        # Create user directly without OTP
        try:
            new_user = User(
                name=name,
                email=email,
                phone=phone,
                state=state,
                district=district,
                farm_size=float(farm_size) if farm_size else 0.0,
                password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
                is_verified=True # Auto-verify
            )
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user)
            flash('Registration successful! Welcome to AgriSmart.', 'success')
            return redirect(url_for('dashboard.home'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            if not user.is_verified:
                flash('Please verify your account first.', 'warning')
                return redirect(url_for('auth.register'))
            
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=True)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard.home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
