from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.database import db
from models.bill import Bill
from models.student import Student
from datetime import datetime, date, timedelta
from flask import current_app
from controllers.auth_controller import login_required, admin_required
from utils.email_notifier import notifier
import json

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/overdue')
@login_required
@admin_required
def check_overdue():
    """Check and display overdue bills"""
    from datetime import date
    
    # Find bills overdue by more than 7 days
    overdue_date = date.today() - timedelta(days=7)
    overdue_bills = Bill.query.filter(
        Bill.status.in_(['unpaid', 'partial']),
        Bill.due_date < overdue_date
    ).join(Student).all()
    
    # Calculate totals
    total_overdue = sum(bill.balance() for bill in overdue_bills)
    total_students = len(set(bill.student_id for bill in overdue_bills))
    
    # Group by student for display
    students_with_overdue = {}
    for bill in overdue_bills:
        if bill.balance() > 0:
            if bill.student.id not in students_with_overdue:
                students_with_overdue[bill.student.id] = {
                    'student': bill.student,
                    'bills': [],
                    'total_overdue': 0
                }
            students_with_overdue[bill.student.id]['bills'].append(bill)
            students_with_overdue[bill.student.id]['total_overdue'] += bill.balance()
    
    return render_template('notifications/overdue.html',
                         students_with_overdue=students_with_overdue,
                         total_overdue=total_overdue,
                         total_students=total_students,
                         today=date.today())

@notification_bp.route('/send_overdue', methods=['POST'])
@login_required
@admin_required
def send_overdue_notifications():
    """Send overdue notifications"""
    try:
        results = notifier.check_overdue_bills()
        
        if results:
            flash(f'Sent {len(results)} overdue notifications', 'success')
            return jsonify({
                'success': True,
                'message': f'Sent {len(results)} notifications',
                'results': results
            })
        else:
            flash('No overdue notifications to send', 'info')
            return jsonify({
                'success': True,
                'message': 'No overdue notifications to send'
            })
            
    except Exception as e:
        flash(f'Error sending notifications: {str(e)}', 'danger')
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@notification_bp.route('/settings')
@login_required
@admin_required
def notification_settings():
    """Display notification settings"""
    return render_template('notifications/settings.html',
                         enabled=notifier.enabled,
                         from_email=notifier.from_email)

@notification_bp.route('/test_email', methods=['POST'])
@login_required
@admin_required
def test_email():
    """Send a test email"""
    try:
        # Get first student with email
        student = Student.query.filter(Student.email != '').first()
        
        if not student:
            flash('No students with email addresses found', 'warning')
            return redirect(url_for('notification.notification_settings'))
        
        # Create test bill
        from datetime import date
        test_bill = Bill(
            student_id=student.id,
            description='Test Bill - Overdue Notification',
            amount=100.00,
            due_date=date.today() - timedelta(days=10),
            status='unpaid'
        )
        
        # Send test notification
        if notifier.send_overdue_notification(student, [test_bill]):
            flash(f'Test email sent to {student.email}', 'success')
        else:
            flash('Failed to send test email. Check SMTP settings.', 'danger')
            
    except Exception as e:
        flash(f'Error sending test email: {str(e)}', 'danger')
    
    return redirect(url_for('notification.notification_settings'))


