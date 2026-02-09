import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-this'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database/school_billing.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
