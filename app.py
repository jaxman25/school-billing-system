from flask import Flask, render_template, session, redirect, url_for
from models.database import db, init_db
import os
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
    
    # Fix database path for Windows
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'database', 'school_billing.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    from controllers.auth_controller import auth_bp
    from controllers.student_controller import student_bp
    from controllers.bill_controller import bill_bp
    from controllers.payment_controller import payment_bp
    from controllers.report_controller import report_bp
    from controllers.notification_controller import notification_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/students')
    app.register_blueprint(bill_bp, url_prefix='/bills')
    app.register_blueprint(payment_bp, url_prefix='/payments')
    app.register_blueprint(report_bp, url_prefix='/reports')
    app.register_blueprint(notification_bp, url_prefix='/notifications')
    
    # Import authentication decorators
    from controllers.auth_controller import login_required, admin_required
    
    @app.route('/')
    @login_required
    def index():
        # Quick dashboard stats
        from models.student import Student
        from models.bill import Bill
        from models.payment import Payment
        from sqlalchemy import func
        from datetime import datetime, date, timedelta
        
        total_students = Student.query.count()
        unpaid_bills = Bill.query.filter_by(status='unpaid').count()
        
        # Calculate total outstanding
        total_outstanding = db.session.query(func.sum(Bill.amount)).filter_by(status='unpaid').scalar()
        total_outstanding = total_outstanding if total_outstanding else 0
        
        # Get recent unpaid bills
        recent_unpaid = Bill.query.filter_by(status='unpaid').order_by(Bill.due_date).limit(5).all()
        
        # Chart data - Bill Status Distribution
        paid_count = Bill.query.filter_by(status='paid').count()
        unpaid_count = Bill.query.filter_by(status='unpaid').count()
        partial_count = Bill.query.filter_by(status='partial').count()
        bill_stats = [paid_count, unpaid_count, partial_count]
        
        # Chart data - Monthly Collections (last 6 months)
        monthly_data = []
        monthly_labels = []
        today = date.today()
        
        for i in range(5, -1, -1):
            # Calculate start of month (going back i months)
            target_month = today.month - i
            target_year = today.year
            
            if target_month <= 0:
                target_month += 12
                target_year -= 1
            
            month_start = date(target_year, target_month, 1)
            
            # Calculate end of month
            if target_month == 12:
                month_end = date(target_year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(target_year, target_month + 1, 1) - timedelta(days=1)
            
            # Get monthly total
            monthly_total = db.session.query(func.sum(Payment.amount)).filter(
                Payment.payment_date >= month_start,
                Payment.payment_date <= month_end
            ).scalar() or 0
            
            monthly_data.append(float(monthly_total))
            monthly_labels.append(month_start.strftime('%b %Y'))
        
        # Chart data - Top 5 Students with Outstanding
        top_students = []
        for student in Student.query.all():
            outstanding = student.total_outstanding()
            if outstanding > 0:
                top_students.append({
                    'name': student.name,
                    'outstanding': outstanding
                })
        
        top_students.sort(key=lambda x: x['outstanding'], reverse=True)
        top_5_students = top_students[:5]
        
        top_students_labels = [s['name'] for s in top_5_students]
        top_students_data = [float(s['outstanding']) for s in top_5_students]
        
        return render_template('index.html',
                             total_students=total_students,
                             unpaid_bills=unpaid_bills,
                             total_outstanding=total_outstanding,
                             recent_unpaid=recent_unpaid,
                             username=session.get('username'),
                             role=session.get('role'),
                             bill_stats=bill_stats,
                             monthly_labels=monthly_labels,
                             monthly_data=monthly_data,
                             top_students_labels=top_students_labels,
                             top_students_data=top_students_data)
    
    @app.before_request
    def before_request():
        # Make username available to all templates
        from flask import g
        g.username = session.get('username')
        g.role = session.get('role')
    
    return app

def create_default_admin():
    """Create default admin user if none exists"""
    from models.user import User
    from app import create_app
    
    app = create_app()
    with app.app_context():
        if User.query.count() == 0:
            admin = User(
                username='admin',
                email='admin@school.edu',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print(" Default admin user created: admin / admin123")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        # Create default admin user
        create_default_admin()
    
    print(" Starting School Billing System MPV...")
    print(" Authentication: Enabled")
    print(" Default admin: admin / admin123")
    print(" Application available at: http://localhost:5000")
    print(" Database: database/school_billing.db")
    print(" Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
