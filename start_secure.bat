Write-Host " DEPLOYING COMPLETE SECURITY SUITE" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# 1. Install all dependencies
Write-Host "`n Installing security dependencies..." -ForegroundColor Yellow
.\venv\Scripts\activate
pip install cryptography pysqlcipher3 flask-limiter flask-talisman

# 2. Create SSL directory and certs
Write-Host "`n Setting up SSL..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "ssl" -Force
New-Item -ItemType Directory -Path "database/backups" -Force
New-Item -ItemType Directory -Path "database/encrypted" -Force

# 3. Generate security configuration
Write-Host "`n Creating security configuration..." -ForegroundColor Yellow
@"
# PRODUCTION SECURITY CONFIGURATION
SECRET_KEY=$(New-Guid).ToString()
DEBUG=False
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
PERMANENT_SESSION_LIFETIME=3600

# SSL Configuration (uncomment for production)
# SSL_CERT_PATH=ssl/cert.pem
# SSL_KEY_PATH=ssl/key.pem
# SSL_PASSWORD=your-secure-password

# Database Encryption
DB_ENCRYPTION_KEY_PATH=database/encryption.key
DB_ENCRYPTION_ENABLED=True

# WAF Configuration
WAF_ENABLED=True
WAF_BLOCK_THRESHOLD=5
WAF_BLOCK_DURATION=3600
"@ | Out-File -FilePath ".env.production" -Encoding UTF8

# 4. Create startup script with all security features
Write-Host "`n Creating secure startup script..." -ForegroundColor Yellow
@'
@echo off
echo ========================================
echo   SCHOOL BILLING SYSTEM - SECURE START
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Check security requirements
python -c "
import sys
try:
    import cryptography
    import flask_talisman
    import flask_limiter
    print(' All security packages installed')
except ImportError as e:
    print(f' Missing package: {e}')
    sys.exit(1)
"

REM Check SSL certificate
if not exist "ssl\cert.pem" (
    echo   SSL certificate not found
    echo Creating self-signed certificate...
    python -c "
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime

# Generate key
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

# Generate certificate
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u'US'),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u'State'),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u'City'),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u'School Billing System'),
    x509.NameAttribute(NameOID.COMMON_NAME, u'school-billing.local'),
])

cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    datetime.datetime.utcnow() + datetime.timedelta(days=365)
).add_extension(
    x509.SubjectAlternativeName([x509.DNSName(u'localhost')]),
    critical=False,
).sign(key, hashes.SHA256())

# Write certificate
with open('ssl/cert.pem', 'wb') as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

# Write private key
with open('ssl/key.pem', 'wb') as f:
    f.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

print(' Self-signed certificate created')
"
)

REM Start with all security features
echo.
echo   Starting with security features:
echo     HTTPS/SSL
echo     Rate Limiting
echo     Web Application Firewall
echo     Database Encryption
echo     Security Headers
echo.
echo  Access at: https://localhost:5000
echo   Accept self-signed certificate warning
echo.

python app.py
pause
