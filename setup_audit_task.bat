@echo off
REM Security Audit Scheduled Task Script
echo Creating scheduled security audit task...

REM Create task to run weekly security audit
schtasks /create /tn "School Billing Security Audit" ^
  /tr "C:\Users\KONZA\school_billing_mpv\run_audit.bat" ^
  /sc weekly /d MON /st 02:00 ^
  /ru SYSTEM ^
  /rl HIGHEST

REM Create batch file to run audit
echo @echo off > run_audit.bat
echo cd /d "C:\Users\KONZA\school_billing_mpv" >> run_audit.bat
echo call venv\Scripts\activate >> run_audit.bat
echo python security_audit.py >> run_audit.bat
echo exit >> run_audit.bat

echo  Security audit task created!
echo Task runs every Monday at 2:00 AM
echo Reports saved to: security_audit_YYYYMMDD_HHMMSS.json
pause
