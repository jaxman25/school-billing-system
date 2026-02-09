from fpdf import FPDF
from datetime import datetime
import os

class PDFReport(FPDF):
    def header(self):
        # Logo
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'SCHOOL BILLING SYSTEM', 0, 1, 'C')
        self.set_font('Arial', '', 12)
        self.cell(0, 10, 'Official Report', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)
    
    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

def generate_outstanding_pdf(student_data, total_outstanding):
    pdf = PDFReport()
    pdf.add_page()
    
    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'OUTSTANDING PAYMENTS REPORT', 0, 1, 'C')
    pdf.ln(5)
    
    # Report info
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1)
    pdf.cell(0, 10, f'Total Outstanding: ${total_outstanding:.2f}', 0, 1)
    pdf.ln(10)
    
    # Student details
    for data in student_data:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f'Student: {data["student"].name} (Grade {data["student"].grade})', 0, 1)
        
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, f'Guardian: {data["student"].guardian_name}', 0, 1)
        pdf.cell(0, 8, f'Phone: {data["student"].phone}', 0, 1)
        pdf.cell(0, 8, f'Total Outstanding: ${data["outstanding"]:.2f}', 0, 1)
        pdf.ln(5)
        
        # Bills table
        if data["unpaid_bills"]:
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(40, 10, 'Description', 1)
            pdf.cell(30, 10, 'Amount', 1)
            pdf.cell(30, 10, 'Paid', 1)
            pdf.cell(30, 10, 'Balance', 1)
            pdf.cell(30, 10, 'Due Date', 1)
            pdf.ln()
            
            pdf.set_font('Arial', '', 10)
            for bill in data["unpaid_bills"]:
                pdf.cell(40, 10, bill.description[:30], 1)
                pdf.cell(30, 10, f'${bill.amount:.2f}', 1)
                pdf.cell(30, 10, f'${bill.amount_paid():.2f}', 1)
                pdf.cell(30, 10, f'${bill.balance():.2f}', 1)
                pdf.cell(30, 10, str(bill.due_date), 1)
                pdf.ln()
        
        pdf.ln(10)
    
    # Create exports directory if it doesn't exist
    os.makedirs('exports/reports', exist_ok=True)
    
    # Save PDF
    filename = f'exports/reports/outstanding_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    pdf.output(filename)
    return filename

def generate_collections_pdf(today_payments, today_total, month_payments, month_total):
    pdf = PDFReport()
    pdf.add_page()
    
    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'COLLECTIONS REPORT', 0, 1, 'C')
    pdf.ln(5)
    
    # Report info
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1)
    pdf.ln(10)
    
    # Summary
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Summary', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Today\'s Collections: ${today_total:.2f}', 0, 1)
    pdf.cell(0, 10, f'This Month\'s Collections: ${month_total:.2f}', 0, 1)
    pdf.ln(10)
    
    # Today's payments
    if today_payments:
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f'Today\'s Payments ({len(today_payments)})', 0, 1)
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(40, 10, 'Receipt #', 1)
        pdf.cell(30, 10, 'Bill ID', 1)
        pdf.cell(30, 10, 'Amount', 1)
        pdf.cell(40, 10, 'Method', 1)
        pdf.cell(30, 10, 'Time', 1)
        pdf.ln()
        
        pdf.set_font('Arial', '', 10)
        for payment in today_payments:
            pdf.cell(40, 10, payment.receipt_no, 1)
            pdf.cell(30, 10, str(payment.bill_id), 1)
            pdf.cell(30, 10, f'${payment.amount:.2f}', 1)
            pdf.cell(40, 10, payment.payment_method.upper(), 1)
            pdf.cell(30, 10, payment.created_at.strftime("%H:%M"), 1)
            pdf.ln()
    
    pdf.ln(10)
    
    # Create exports directory if it doesn't exist
    os.makedirs('exports/reports', exist_ok=True)
    
    # Save PDF
    filename = f'exports/reports/collections_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    pdf.output(filename)
    return filename

def generate_receipt_pdf(payment):
    pdf = PDFReport()
    pdf.add_page()
    
    # Header
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 15, 'OFFICIAL RECEIPT', 0, 1, 'C')
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'SCHOOL BILLING SYSTEM', 0, 1, 'C')
    pdf.ln(10)
    
    # Receipt details
    pdf.set_font('Arial', '', 12)
    pdf.cell(50, 10, 'Receipt Number:', 0, 0)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, payment.receipt_no, 0, 1)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(50, 10, 'Date:', 0, 0)
    pdf.cell(0, 10, payment.payment_date.strftime("%Y-%m-%d"), 0, 1)
    
    pdf.cell(50, 10, 'Payment Method:', 0, 0)
    pdf.cell(0, 10, payment.payment_method.upper(), 0, 1)
    
    pdf.ln(10)
    
    # Payment details box
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, pdf.get_y(), 190, 30, 'F')
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 15, 'PAYMENT DETAILS', 0, 1, 'C')
    
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'Amount: ${payment.amount:.2f}', 0, 1, 'C')
    
    pdf.ln(15)
    
    # Additional info
    pdf.set_font('Arial', '', 12)
    pdf.cell(50, 10, 'Bill ID:', 0, 0)
    pdf.cell(0, 10, str(payment.bill_id), 0, 1)
    
    if payment.notes:
        pdf.cell(50, 10, 'Notes:', 0, 0)
        pdf.multi_cell(0, 10, payment.notes)
    
    pdf.ln(20)
    
    # Footer
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, 'Thank you for your payment!', 0, 1, 'C')
    pdf.cell(0, 10, 'Generated by School Billing System', 0, 1, 'C')
    
    # Create receipts directory if it doesn't exist
    os.makedirs('exports/receipts', exist_ok=True)
    
    # Save PDF
    filename = f'exports/receipts/{payment.receipt_no}.pdf'
    pdf.output(filename)
    return filename
