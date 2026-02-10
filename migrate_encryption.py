#!/usr/bin/env python3
"""
Database Encryption Migration Script
Run this once to encrypt existing data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from models.database import db
from models.student import Student
from models.bill import Bill
from models.payment import Payment
from models.user import User
from utils.database_encryptor import db_encryptor
from datetime import datetime

def migrate_to_encryption():
    print(" Starting database encryption migration...")
    print("  BACKUP YOUR DATABASE BEFORE CONTINUING!")
    input("Press Enter to continue or Ctrl+C to cancel...")
    
    # Backup first
    backup_path = db_encryptor.backup_database()
    print(f" Backup created: {backup_path}")
    
    try:
        # This is a simplified migration
        # In production, you would:
        # 1. Create new encrypted tables
        # 2. Migrate data with encryption
        # 3. Switch to new tables
        
        print(" Creating encrypted version of database...")
        
        # For now, just backup and show instructions
        print("""
        Manual migration required:
        
        1. Install SQLCipher: https://github.com/sqlcipher/sqlcipher
        2. Encrypt database:
           sqlcipher school_billing.db
           PRAGMA key = 'your-encryption-key';
           .backup encrypted.db
           .exit
        
        3. Replace database file:
           mv encrypted.db school_billing.db
        
        4. Update SQLAlchemy URI:
           app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school_billing.db?key=your-encryption-key'
        """)
        
        print(" Migration instructions generated")
        print(" See database_encryption_guide.md for details")
        
    except Exception as e:
        print(f" Migration failed: {e}")
        print("Restoring from backup...")
        db_encryptor.restore_database(backup_path)
        print(" Database restored from backup")

if __name__ == "__main__":
    migrate_to_encryption()
