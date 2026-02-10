import sqlite3
from cryptography.fernet import Fernet
import base64
import os
from pathlib import Path

class DatabaseEncryptor:
    def __init__(self, db_path="database/school_billing.db", key_file="database/encryption.key"):
        self.db_path = db_path
        self.key_file = key_file
        self.key = self._load_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _load_or_create_key(self):
        """Load existing key or create new one"""
        key_path = Path(self.key_file)
        
        if key_path.exists():
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            key_path.parent.mkdir(parents=True, exist_ok=True)
            with open(key_path, 'wb') as f:
                f.write(key)
            # Secure the key file
            try:
                import win32api
                import win32con
                win32api.SetFileAttributes(self.key_file, win32con.FILE_ATTRIBUTE_HIDDEN)
            except:
                pass
            return key
    
    def encrypt_value(self, value):
        """Encrypt a string value"""
        if value is None:
            return None
        return self.cipher.encrypt(str(value).encode()).decode()
    
    def decrypt_value(self, encrypted_value):
        """Decrypt a string value"""
        if encrypted_value is None:
            return None
        try:
            return self.cipher.decrypt(encrypted_value.encode()).decode()
        except:
            return encrypted_value  # Return as-is if not encrypted
    
    def create_encrypted_connection(self):
        """Create SQLite connection with encryption hooks"""
        conn = sqlite3.connect(self.db_path)
        
        # Add encryption/decryption functions to SQLite
        conn.create_function("ENCRYPT", 1, self.encrypt_value)
        conn.create_function("DECRYPT", 1, self.decrypt_value)
        
        return conn
    
    def backup_database(self, backup_path=None):
        """Create encrypted backup of database"""
        if backup_path is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"database/backups/school_billing_{timestamp}.db.enc"
        
        Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Read entire database file and encrypt it
        with open(self.db_path, 'rb') as f:
            db_data = f.read()
        
        encrypted_data = self.cipher.encrypt(db_data)
        
        with open(backup_path, 'wb') as f:
            f.write(encrypted_data)
        
        return backup_path
    
    def restore_database(self, backup_path):
        """Restore database from encrypted backup"""
        with open(backup_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = self.cipher.decrypt(encrypted_data)
        
        # Backup current database first
        current_backup = f"database/backups/pre_restore_{os.path.basename(backup_path)}"
        self.backup_database(current_backup)
        
        # Write decrypted data
        with open(self.db_path, 'wb') as f:
            f.write(decrypted_data)
        
        return True

# Create global instance
db_encryptor = DatabaseEncryptor()
