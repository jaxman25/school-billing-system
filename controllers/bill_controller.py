from controllers.auth_controller import login_required


from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.database import db
from models.student import Student
from models.bill import Bill
from models.payment import Payment
from datetime import datetime

bill_bp = Blueprint('bill', __name__)

@login_required
@login_required
@bill_bp.route('/')
def list_bills():
    bills = Bill.query.all()
    return render_template('bills/list.html', bills=bills)

@login_required
@login_required
@bill_bp.route('/create', methods=['GET', 'POST'])
def create_bill():
    if request.method == 'POST':
        try:
            bill = Bill(
                student_id=int(request.form['student_id']),
                description=request.form['description'],
                amount=float(request.form['amount']),
                due_date=datetime.strptime(request.form['due_date'], '%Y-%m-%d').date(),
                status='unpaid'
            )
            db.session.add(bill)
            db.session.commit()
            flash('Bill created successfully!', 'success')
            return redirect(url_for('bill.list_bills'))
        except Exception as e:
            flash(f'Error creating bill: {str(e)}', 'danger')
    
    students = Student.query.all()
    return render_template('bills/create.html', students=students)

@login_required
@login_required
@bill_bp.route('/unpaid')
def unpaid_bills():
    unpaid = Bill.query.filter(Bill.status.in_(['unpaid', 'partial'])).join(Student).all()
    return render_template('bills/unpaid.html', bills=unpaid)

@login_required
@login_required
@bill_bp.route('/mark_paid/<int:bill_id>', methods=['POST'])
def mark_bill_paid(bill_id):
    try:
        bill = Bill.query.get_or_404(bill_id)
        
        # Create a payment for the remaining balance
        balance = bill.balance()
        if balance > 0:
            payment = Payment(
                bill_id=bill_id,
                amount=balance,
                payment_method='manual',
                notes='Marked as paid manually by admin'
            )
            db.session.add(payment)
        
        bill.status = 'paid'
        db.session.commit()
        flash(f'Bill #{bill_id} marked as paid successfully!', 'success')
    except Exception as e:
        flash(f'Error marking bill as paid: {str(e)}', 'danger')
    
    return redirect(url_for('bill.list_bills'))

@login_required
@login_required
@bill_bp.route('/delete/<int:bill_id>', methods=['POST'])
def delete_bill(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    db.session.delete(bill)
    db.session.commit()
    flash('Bill deleted successfully!', 'success')
    return redirect(url_for('bill.list_bills'))

@login_required
@login_required
@bill_bp.route('/bulk', methods=['GET'])
def bulk_create_page():
    students = Student.query.all()
    return render_template('bills/bulk.html', students=students)

@login_required
@login_required
@bill_bp.route('/bulk_create', methods=['POST'])
def bulk_create():
    try:
        student_ids = request.form.getlist('student_ids')
        description = request.form['description']
        amount = float(request.form['amount'])
        due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
        
        if not student_ids:
            flash('Please select at least one student', 'warning')
            return redirect(url_for('bill.bulk_create_page'))
        
        bills_created = 0
        for student_id in student_ids:
            bill = Bill(
                student_id=int(student_id),
                description=description,
                amount=amount,
                due_date=due_date,
                status='unpaid'
            )
            db.session.add(bill)
            bills_created += 1
        
        db.session.commit()
        flash(f'Successfully created {bills_created} bills for "{description}"', 'success')
        return redirect(url_for('bill.list_bills'))
        
    except Exception as e:
        flash(f'Error creating bulk bills: {str(e)}', 'danger')
        return redirect(url_for('bill.bulk_create_page'))

@login_required
@login_required
@bill_bp.route('/search', methods=['GET'])
def search_bills():
    query = request.args.get('query', '').strip()
    status = request.args.get('status', '')
    min_amount = request.args.get('min_amount', '')
    max_amount = request.args.get('max_amount', '')
    due_date_from = request.args.get('due_date_from', '')
    due_date_to = request.args.get('due_date_to', '')
    
    # Start with base query
    bills_query = Bill.query.join(Student)
    
    # Apply filters
    if query:
        bills_query = bills_query.filter(
            (Student.name.ilike(f'%{query}%')) | 
            (Bill.description.ilike(f'%{query}%'))
        )
    
    if status:
        bills_query = bills_query.filter(Bill.status == status)
    
    if min_amount:
        bills_query = bills_query.filter(Bill.amount >= float(min_amount))
    
    if max_amount:
        bills_query = bills_query.filter(Bill.amount <= float(max_amount))
    
    if due_date_from:
        bills_query = bills_query.filter(Bill.due_date >= datetime.strptime(due_date_from, '%Y-%m-%d').date())
    
    if due_date_to:
        bills_query = bills_query.filter(Bill.due_date <= datetime.strptime(due_date_to, '%Y-%m-%d').date())
    
    bills = bills_query.all()
    
    return render_template('bills/search.html', 
                         bills=bills,
                         query=query,
                         status=status,
                         min_amount=min_amount,
                         max_amount=max_amount,
                         due_date_from=due_date_from,
                         due_date_to=due_date_to)


