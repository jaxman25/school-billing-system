from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db():
    # Import models here to avoid circular imports
    from models.student import Student
    from models.bill import Bill
    from models.payment import Payment
    
    # Create all tables
    db.create_all()
    
    # Add sample data for testing
    if Student.query.count() == 0:
        print("Adding sample data...")
        
        # Create sample student
        sample_student = Student(
            name="John Doe",
            grade="10",
            guardian_name="Jane Doe",
            phone="123-456-7890",
            email="parent@example.com"
        )
        db.session.add(sample_student)
        db.session.commit()
        
        # Create sample bill
        from datetime import date, timedelta
        sample_bill = Bill(
            student_id=1,
            description="Term 1 Tuition",
            amount=500.00,
            due_date=date.today() + timedelta(days=30),
            status='unpaid'
        )
        db.session.add(sample_bill)
        db.session.commit()
        
        print("Sample data added successfully!")
