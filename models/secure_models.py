import sqlite3
from utils.database_encryptor import db_encryptor

class SecureStudent:
    """Wrapper for encrypted student operations"""
    
    @staticmethod
    def get_all():
        conn = db_encryptor.create_encrypted_connection()
        cursor = conn.cursor()
        
        # Example of encrypted query
        cursor.execute('''
            SELECT 
                id,
                DECRYPT(name) as name,
                DECRYPT(grade) as grade,
                DECRYPT(guardian_name) as guardian_name,
                DECRYPT(phone) as phone,
                DECRYPT(email) as email,
                created_at
            FROM students
        ''')
        
        students = cursor.fetchall()
        conn.close()
        return students
    
    @staticmethod
    def create(name, grade, guardian_name, phone, email):
        conn = db_encryptor.create_encrypted_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO students (name, grade, guardian_name, phone, email)
            VALUES (ENCRYPT(?), ENCRYPT(?), ENCRYPT(?), ENCRYPT(?), ENCRYPT(?))
        ''', (name, grade, guardian_name, phone, email))
        
        conn.commit()
        student_id = cursor.lastrowid
        conn.close()
        return student_id

# Update existing models to use encryption
# In models/student.py, models/bill.py, models/payment.py, models/user.py
# Replace direct SQLAlchemy with encrypted version or add encryption hooks
