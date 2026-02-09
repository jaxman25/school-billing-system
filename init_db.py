import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app

app = create_app()

with app.app_context():
    from models.database import init_db
    init_db()
    print(" Database initialized successfully!")
    print(f"Database file: {os.path.abspath('database/school_billing.db')}")
