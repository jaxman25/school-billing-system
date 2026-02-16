from models.database import db
from datetime import datetime

class Bill(db.Model):
    __tablename__ = 'bills'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='unpaid')  # unpaid, paid, partial
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with payments
    payments = db.relationship('Payment', backref='bill', lazy=True, cascade='all, delete-orphan')
    
    def amount_paid(self):
        return sum(payment.amount for payment in self.payments)
    
    def balance(self):
        return self.amount - self.amount_paid()
    
    def update_status(self):
        paid_amount = self.amount_paid()
        if paid_amount >= self.amount:
            self.status = 'paid'
        elif paid_amount > 0:
            self.status = 'partial'
        else:
            self.status = 'unpaid'
        return self.status
    
    def __repr__(self):
        return f'<Bill {self.description}: >'
