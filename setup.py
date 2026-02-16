import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, create_default_admin

print(" Setting up School Billing System with Advanced Features...")
print("=" * 60)

app = create_app()
with app.app_context():
    from models.database import db
    from models.user import User
    
    # Create all tables
    db.create_all()
    print(" Database tables created")
    
    # Create default admin user
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
    else:
        print(" Admin user already exists")
    
    # Create exports directories
    os.makedirs('exports/reports', exist_ok=True)
    os.makedirs('exports/receipts', exist_ok=True)
    os.makedirs('templates/notifications', exist_ok=True)
    os.makedirs('templates/partials', exist_ok=True)
    print(" Created required directories")
    
    print("=" * 60)
    print(" Setup complete!")
    print("\n To start the application:")
    print("   1. python app.py")
    print("   2. Open: http://localhost:5000")
    print("   3. Login with: admin / admin123")
    print("\n NEW FEATURES ADDED:")
    print("     User authentication with roles")
    print("     PDF export for reports")
    print("     Email notifications for overdue bills")
    print("     Interactive dashboard charts")
