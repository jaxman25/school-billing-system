#!/usr/bin/env python3
"""
School Billing System - Security Audit Tool
Run this weekly to check system security
"""

import os
import sys
import subprocess
import datetime
import json
from pathlib import Path

class SecurityAudit:
    def __init__(self):
        self.report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "checks": [],
            "score": 0,
            "total_checks": 0,
            "status": "PASS"
        }
    
    def check_file_permissions(self):
        """Check file and directory permissions"""
        check = {
            "name": "File Permissions",
            "status": "PASS",
            "issues": []
        }
        
        critical_files = [
            "database/school_billing.db",
            ".env",
            "database/encryption.key"
        ]
        
        for file in critical_files:
            if os.path.exists(file):
                try:
                    # Check if file is readable by others
                    stat = os.stat(file)
                    if stat.st_mode & 0o004:  # Others can read
                        check["issues"].append(f"{file}: World-readable")
                        check["status"] = "FAIL"
                except:
                    pass
        
        self.report["checks"].append(check)
    
    def check_dependencies(self):
        """Check for outdated/vulnerable dependencies"""
        check = {
            "name": "Dependencies",
            "status": "PASS",
            "issues": []
        }
        
        try:
            # Check pip packages for known vulnerabilities
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                outdated = json.loads(result.stdout)
                if outdated:
                    check["issues"].extend([pkg["name"] for pkg in outdated])
                    check["status"] = "WARN"
        
        except:
            check["issues"].append("Could not check dependencies")
            check["status"] = "ERROR"
        
        self.report["checks"].append(check)
    
    def check_ssl_configuration(self):
        """Check SSL/TLS configuration"""
        check = {
            "name": "SSL Configuration",
            "status": "PASS",
            "issues": []
        }
        
        ssl_files = ["ssl/cert.pem", "ssl/key.pem", "ssl/cert.pfx"]
        ssl_exists = any(os.path.exists(f) for f in ssl_files)
        
        if not ssl_exists:
            check["issues"].append("No SSL certificate found")
            check["status"] = "FAIL"
        
        # Check certificate expiration (simplified)
        for ssl_file in ssl_files:
            if os.path.exists(ssl_file):
                # In production, use cryptography library to check dates
                file_age = datetime.datetime.fromtimestamp(
                    os.path.getmtime(ssl_file)
                )
                age_days = (datetime.datetime.now() - file_age).days
                
                if age_days > 365:  # Cert older than 1 year
                    check["issues"].append(f"{ssl_file}: Certificate may be expired ({age_days} days old)")
                    check["status"] = "WARN"
        
        self.report["checks"].append(check)
    
    def check_database_backup(self):
        """Check database backup status"""
        check = {
            "name": "Database Backup",
            "status": "PASS",
            "issues": []
        }
        
        backup_dir = Path("database/backups")
        if backup_dir.exists():
            backups = list(backup_dir.glob("*.db*"))
            if backups:
                latest_backup = max(backups, key=os.path.getmtime)
                backup_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(
                    latest_backup.stat().st_mtime
                )
                
                if backup_age.days > 7:
                    check["issues"].append(f"Last backup: {backup_age.days} days ago")
                    check["status"] = "WARN"
            else:
                check["issues"].append("No backups found")
                check["status"] = "FAIL"
        else:
            check["issues"].append("Backup directory doesn't exist")
            check["status"] = "FAIL"
        
        self.report["checks"].append(check)
    
    def check_user_accounts(self):
        """Check user account security"""
        check = {
            "name": "User Accounts",
            "status": "PASS",
            "issues": []
        }
        
        try:
            from models.user import User
            from models.database import db
            from app import create_app
            
            app = create_app()
            with app.app_context():
                users = User.query.all()
                
                # Check for default admin password
                for user in users:
                    if user.username == "admin":
                        # Check if password might be default
                        # This is a simplified check
                        check["issues"].append("Default admin account exists - ensure password changed")
                        check["status"] = "WARN"
                
                # Check for inactive users
                inactive = [u.username for u in users if not u.is_active]
                if inactive:
                    check["issues"].append(f"Inactive users: {', '.join(inactive)}")
        
        except Exception as e:
            check["issues"].append(f"Could not check users: {e}")
            check["status"] = "ERROR"
        
        self.report["checks"].append(check)
    
    def run_all_checks(self):
        """Run all security checks"""
        print(" Running Security Audit...")
        print("=" * 50)
        
        self.check_file_permissions()
        self.check_dependencies()
        self.check_ssl_configuration()
        self.check_database_backup()
        self.check_user_accounts()
        
        # Calculate score
        total = len(self.report["checks"])
        passed = sum(1 for c in self.report["checks"] if c["status"] == "PASS")
        self.report["score"] = int((passed / total) * 100) if total > 0 else 0
        
        # Overall status
        if any(c["status"] == "FAIL" for c in self.report["checks"]):
            self.report["status"] = "FAIL"
        elif any(c["status"] == "WARN" for c in self.report["checks"]):
            self.report["status"] = "WARN"
        
        return self.report
    
    def generate_report(self):
        """Generate formatted report"""
        report_file = f"security_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, "w") as f:
            json.dump(self.report, f, indent=2)
        
        # Print summary
        print("\n SECURITY AUDIT SUMMARY")
        print("=" * 50)
        print(f"Overall Status: {self.report['status']}")
        print(f"Security Score: {self.report['score']}%")
        print(f"Report saved to: {report_file}")
        
        print("\n Detailed Results:")
        for check in self.report["checks"]:
            status_icon = "" if check["status"] == "PASS" else " " if check["status"] == "WARN" else ""
            print(f"{status_icon} {check['name']}: {check['status']}")
            for issue in check["issues"]:
                print(f"    {issue}")
        
        print("\n Recommendations:")
        if self.report["status"] != "PASS":
            print("1. Fix all FAIL issues immediately")
            print("2. Address WARN issues within 7 days")
            print("3. Schedule weekly security audits")
            print("4. Consider professional penetration testing")
        
        return report_file

def main():
    audit = SecurityAudit()
    audit.run_all_checks()
    audit.generate_report()

if __name__ == "__main__":
    main()
