from flask import Blueprint, render_template, send_file, flash
from models.database import db
from models.student import Student
from models.bill import Bill
from models.payment import Payment
from datetime import datetime, date
from sqlalchemy import func
from controllers.auth_controller import login_required
from utils.pdf_exporter import generate_outstanding_pdf, generate_collections_pdf
import os

report_bp = Blueprint('report', __name__)

@report_bp.route('/outstanding')
@login_required
def outstanding():
    # Get all students with outstanding bills
    students = Student.query.all()
    
    student_data = []
    for student in students:
        outstanding_total = student.total_outstanding()
        if outstanding_total > 0:
            student_data.append({
                'student': student,
                'outstanding': outstanding_total,
                'unpaid_bills': [b for b in student.bills if b.status != 'paid']
            })
    
    # Sort by outstanding amount (highest first)
    student_data.sort(key=lambda x: x['outstanding'], reverse=True)
    
    total_outstanding = sum(s['outstanding'] for s in student_data)
    
    return render_template('reports/outstanding.html', 
                         student_data=student_data, 
                         total_outstanding=total_outstanding)

@report_bp.route('/outstanding/pdf')
@login_required
def outstanding_pdf():
    # Get all students with outstanding bills
    students = Student.query.all()
    
    student_data = []
    for student in students:
        outstanding_total = student.total_outstanding()
        if outstanding_total > 0:
            student_data.append({
                'student': student,
                'outstanding': outstanding_total,
                'unpaid_bills': [b for b in student.bills if b.status != 'paid']
            })
    
    # Sort by outstanding amount (highest first)
    student_data.sort(key=lambda x: x['outstanding'], reverse=True)
    
    total_outstanding = sum(s['outstanding'] for s in student_data)
    
    # Generate PDF
    filename = generate_outstanding_pdf(student_data, total_outstanding)
    
    # Send file for download
    return send_file(
        filename,
        as_attachment=True,
        download_name=f'outstanding_report_{datetime.now().strftime("%Y%m%d")}.pdf',
        mimetype='application/pdf'
    )

@report_bp.route('/collections')
@login_required
def collections():
    today = date.today()
    
    # Today's collections
    today_payments = Payment.query.filter(
        func.date(Payment.payment_date) == today
    ).all()
    
    today_total = sum(p.amount for p in today_payments)
    
    # This month's collections
    month_start = date(today.year, today.month, 1)
    month_payments = Payment.query.filter(
        Payment.payment_date >= month_start
    ).all()
    
    month_total = sum(p.amount for p in month_payments)
    
    return render_template('reports/collections.html',
                         today_payments=today_payments,
                         today_total=today_total,
                         month_payments=month_payments,
                         month_total=month_total)

@report_bp.route('/collections/pdf')
@login_required
def collections_pdf():
    today = date.today()
    
    # Today's collections
    today_payments = Payment.query.filter(
        func.date(Payment.payment_date) == today
    ).all()
    
    today_total = sum(p.amount for p in today_payments)
    
    # This month's collections
    month_start = date(today.year, today.month, 1)
    month_payments = Payment.query.filter(
        Payment.payment_date >= month_start
    ).all()
    
    month_total = sum(p.amount for p in month_payments)
    
    # Generate PDF
    filename = generate_collections_pdf(today_payments, today_total, month_payments, month_total)
    
    # Send file for download
    return send_file(
        filename,
        as_attachment=True,
        download_name=f'collections_report_{datetime.now().strftime("%Y%m%d")}.pdf',
        mimetype='application/pdf'
    )

@report_bp.route('/receipt/pdf/<receipt_no>')
@login_required
def receipt_pdf(receipt_no):
    from utils.pdf_exporter import generate_receipt_pdf
    
    payment = Payment.query.filter_by(receipt_no=receipt_no).first_or_404()
    
    # Generate PDF receipt
    filename = generate_receipt_pdf(payment)
    
    # Send file for download
    return send_file(
        filename,
        as_attachment=True,
        download_name=f'receipt_{receipt_no}.pdf',
        mimetype='application/pdf'
    )
