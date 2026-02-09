print(" Verifying School Billing System Setup...")
print("=" * 50)

import os
import sys

# Check required directories
dirs = ['templates', 'models', 'controllers', 'database']
for d in dirs:
    if os.path.exists(d):
        print(f" Directory exists: {d}")
    else:
        print(f" Missing directory: {d}")
        os.makedirs(d, exist_ok=True)
        print(f"   Created: {d}")

# Check required files
files = ['app.py', 'models/database.py', 'models/student.py', 'models/bill.py', 'models/payment.py']
for f in files:
    if os.path.exists(f):
        print(f" File exists: {f}")
    else:
        print(f" Missing file: {f}")

print("=" * 50)
print(" Installation check complete!")
print("\nTo start the application:")
print("1. Ensure virtual environment is activated")
print("2. Run: python app.py")
print("3. Open browser to: http://localhost:5000")
