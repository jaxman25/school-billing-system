from controllers.auth_controller import login_required


from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.database import db
from models.bill import Bill
from models.payment import Payment
from datetime import datetime

payment_bp = Blueprint('payment', __name__)

@login_required
@login_required
@payment_bp.route('/record', methods=['GET', 'POST'])
def record_payment():
    if request.method == 'POST':
        try:
            bill_id = int(request.form['bill_id'])
            bill = Bill.query.get_or_404(bill_id)
            
            payment_amount = float(request.form['amount'])
            
            # Validate payment amount doesn't exceed balance
            if payment_amount > bill.balance():
                flash(f'Payment amount (${payment_amount:.2f}) exceeds balance (${bill.balance():.2f})', 'danger')
                return redirect(url_for('payment.record_payment'))
            
            payment = Payment(
                bill_id=bill_id,
                amount=payment_amount,
                payment_method=request.form['payment_method'],
                notes=request.form.get('notes', '')
            )
            
            db.session.add(payment)
            
            # Update bill status
            bill.update_status()
            
            db.session.commit()
            flash(f'Payment recorded successfully! Receipt #: {payment.receipt_no}', 'success')
            return redirect(url_for('payment.view_receipt', receipt_no=payment.receipt_no))
        except Exception as e:
            flash(f'Error recording payment: {str(e)}', 'danger')
    
    # Get unpaid bills for dropdown
    unpaid_bills = Bill.query.filter(Bill.status.in_(['unpaid', 'partial'])).all()
    return render_template('payments/record.html', bills=unpaid_bills)

@login_required
@login_required
@payment_bp.route('/receipt/<receipt_no>')
def view_receipt(receipt_no):
    payment = Payment.query.filter_by(receipt_no=receipt_no).first_or_404()
    return render_template('payments/receipt.html', payment=payment)


