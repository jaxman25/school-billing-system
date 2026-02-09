import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os

class EmailNotifier:
    def __init__(self):
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.smtp_username = os.environ.get('SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.from_email = os.environ.get('FROM_EMAIL', 'billing@school.edu')
        self.enabled = bool(self.smtp_username and self.smtp_password)
    
    def send_overdue_notification(self, student, bills):
        """Send overdue notification to student's guardian"""
        if not self.enabled:
            print(" Email notifications disabled - configure SMTP settings")
            return False
        
        try:
            # Prepare email content
            subject = f"Overdue Payment Notice - {student.name}"
            
            # Calculate total overdue
            total_overdue = sum(bill.balance() for bill in bills)
            
            # Create HTML email
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">School Billing System</h2>
                    <h3 style="color: #e74c3c;">Overdue Payment Notice</h3>
                    
                    <p>Dear {student.guardian_name},</p>
                    
                    <p>This is a reminder that the following bills for <strong>{student.name}</strong> are overdue:</p>
                    
                    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                        <thead>
                            <tr style="background-color: #2c3e50; color: white;">
                                <th style="padding: 10px; text-align: left;">Description</th>
                                <th style="padding: 10px; text-align: left;">Due Date</th>
                                <th style="padding: 10px; text-align: left;">Amount Due</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for bill in bills:
                overdue_days = (datetime.now().date() - bill.due_date).days
                html += f"""
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="padding: 10px;">{bill.description}</td>
                                <td style="padding: 10px;">{bill.due_date.strftime('%Y-%m-%d')} ({overdue_days} days overdue)</td>
                                <td style="padding: 10px; color: #e74c3c; font-weight: bold;">${bill.balance():.2f}</td>
                            </tr>
                """
            
            html += f"""
                        </tbody>
                        <tfoot>
                            <tr style="background-color: #f8f9fa;">
                                <td colspan="2" style="padding: 10px; text-align: right;"><strong>Total Overdue:</strong></td>
                                <td style="padding: 10px; color: #e74c3c; font-weight: bold;">${total_overdue:.2f}</td>
                            </tr>
                        </tfoot>
                    </table>
                    
                    <p>Please make the payment at your earliest convenience to avoid any inconvenience.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Payment Methods:</strong></p>
                        <ul>
                            <li>Cash payment at school office</li>
                            <li>Bank transfer (details available at office)</li>
                            <li>Check payable to School Name</li>
                        </ul>
                    </div>
                    
                    <p>If you have already made the payment, please ignore this notice.</p>
                    
                    <p>Best regards,<br>
                    School Billing Office<br>
                    {self.from_email}</p>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version
            text = f"""
            Overdue Payment Notice
            
            Dear {student.guardian_name},
            
            This is a reminder that bills for {student.name} are overdue.
            
            Total Overdue: ${total_overdue:.2f}
            
            Please make payment at your earliest convenience.
            
            School Billing Office
            {self.from_email}
            """
            
            # Send email
            self._send_email(student.email, subject, text, html)
            print(f" Sent overdue notice to {student.email}")
            return True
            
        except Exception as e:
            print(f" Failed to send email: {str(e)}")
            return False
    
    def send_payment_confirmation(self, payment):
        """Send payment confirmation email"""
        if not self.enabled:
            return False
        
        try:
            subject = f"Payment Confirmation - Receipt #{payment.receipt_no}"
            
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #27ae60;">Payment Confirmation</h2>
                    <h3>Receipt #{payment.receipt_no}</h3>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Payment Details:</strong></p>
                        <p>Amount: <span style="color: #27ae60; font-weight: bold;">${payment.amount:.2f}</span></p>
                        <p>Date: {payment.payment_date.strftime('%Y-%m-%d')}</p>
                        <p>Method: {payment.payment_method.upper()}</p>
                        <p>Bill ID: {payment.bill_id}</p>
                    </div>
                    
                    <p>Thank you for your payment!</p>
                    
                    <p>Best regards,<br>
                    School Billing Office<br>
                    {self.from_email}</p>
                </div>
            </body>
            </html>
            """
            
            # Get student email from bill
            from models.bill import Bill
            bill = Bill.query.get(payment.bill_id)
            if bill and bill.student.email:
                self._send_email(bill.student.email, subject, "", html)
                print(f" Sent payment confirmation to {bill.student.email}")
                return True
            
            return False
            
        except Exception as e:
            print(f" Failed to send confirmation: {str(e)}")
            return False
    
    def _send_email(self, to_email, subject, text, html):
        """Send email using SMTP"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = to_email
        
        # Attach both text and HTML versions
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_server, self.smtp_password)
            server.send_message(msg)
    
    def check_overdue_bills(self):
        """Check for overdue bills and send notifications"""
        from models.student import Student
        from models.bill import Bill
        from datetime import date
        
        # Find bills overdue by more than 7 days
        overdue_date = date.today() - timedelta(days=7)
        overdue_bills = Bill.query.filter(
            Bill.status.in_(['unpaid', 'partial']),
            Bill.due_date < overdue_date
        ).all()
        
        # Group by student
        students_with_overdue = {}
        for bill in overdue_bills:
            if bill.student.email and bill.balance() > 0:
                if bill.student.id not in students_with_overdue:
                    students_with_overdue[bill.student.id] = {
                        'student': bill.student,
                        'bills': []
                    }
                students_with_overdue[bill.student.id]['bills'].append(bill)
        
        # Send notifications
        results = []
        for student_id, data in students_with_overdue.items():
            if self.send_overdue_notification(data['student'], data['bills']):
                results.append(f"Sent to {data['student'].name}")
        
        return results

# Create a global instance
notifier = EmailNotifier()
