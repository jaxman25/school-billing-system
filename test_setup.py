import sys
sys.path.insert(0, '.')

from app import create_app
from models.database import db

app = create_app()
with app.app_context():
    from models.student import Student
    from models.bill import Bill
    
    print('=== School Billing System MPV Test ===')
    print(f'Total Students: {Student.query.count()}')
    print(f'Total Bills: {Bill.query.count()}')
    print(f"Unpaid Bills: {Bill.query.filter_by(status='unpaid').count()}")
    print('======================================')
    print('To run the application: python app.py')
    print('Then visit: http://localhost:5000')
