from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.database import db
from models.user import User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # In production, this should be admin-only
            user = User(
                username=request.form['username'],
                email=request.form['email'],
                role=request.form.get('role', 'staff')
            )
            user.set_password(request.form['password'])
            
            db.session.add(user)
            db.session.commit()
            flash('User registered successfully!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error registering user: {str(e)}', 'danger')
    
    return render_template('auth/register.html')

# Authentication decorator
def login_required(f):
    from functools import wraps
    from flask import session, redirect, url_for, flash
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    from flask import session, redirect, url_for, flash
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
